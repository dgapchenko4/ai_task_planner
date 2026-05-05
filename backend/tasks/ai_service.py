import requests
import json
import re
from datetime import datetime, timedelta, date
from django.conf import settings
from typing import Dict, Any, Optional

class YandexGPTService:
    
    def __init__(self):
        self.api_key = settings.YANDEX_GPT_API_KEY
        self.folder_id = settings.YANDEX_GPT_FOLDER_ID
        self.api_url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
        
    def analyze_task(self, task_description: str) -> Dict[str, Any]:
        # Сначала локальный анализ
        local = self._local_analysis(task_description)
        
        # Пробуем API для улучшения
        if self.api_key and self.api_key != 'your-yandex-api-key-here':
            try:
                ai = self._call_api(task_description)
                # Объединяем: дату из локального, остальное из API
                ai['due_date'] = local.get('due_date')
                return ai
            except Exception as e:
                print(f"API error (using local): {e}")
        
        return local
    
    def _call_api(self, task_description: str) -> Dict[str, Any]:
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Api-Key {self.api_key}"
            }
            
            prompt = f"""Проанализируй задачу. Ответь ТОЛЬКО чистым JSON:
{task_description}
{{"summary":"суть","priority":"high/medium/low","estimated_minutes":число,"tags":["тег"]}}"""
            
            body = {
                "modelUri": f"gpt://{self.folder_id}/yandexgpt-lite",
                "completionOptions": {"stream": False, "temperature": 0.3, "maxTokens": "300"},
                "messages": [
                    {"role": "system", "text": "Отвечай только JSON без ```"},
                    {"role": "user", "text": prompt}
                ]
            }
            
            response = requests.post(self.api_url, headers=headers, json=body, timeout=10)
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}")
            
            text = response.json()['result']['alternatives'][0]['message']['text']
            
            # Очистка от ``` и лишнего
            text = text.strip()
            text = re.sub(r'^```(?:json)?\s*\n?', '', text)
            text = re.sub(r'\n?```$', '', text)
            text = text.strip()
            
            # Ищем JSON объект
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                text = match.group()
            
            result = json.loads(text)
            
            # Безопасное извлечение с значениями по умолчанию
            summary = str(result.get('summary', ''))[:200] or task_description[:200]
            priority = result.get('priority', 'medium')
            if priority not in ['high', 'medium', 'low']:
                priority = 'medium'
            
            # Безопасное извлечение минут
            try:
                minutes = int(result.get('estimated_minutes', 0))
                if minutes <= 0:
                    minutes = 60
                minutes = max(1, min(minutes, 1440))
            except (ValueError, TypeError):
                minutes = 60
            
            tags = result.get('tags', [])
            if isinstance(tags, list):
                tags = [str(t) for t in tags[:5]]
            else:
                tags = ['задача']
            
            return {
                "summary": summary,
                "priority": priority,
                "estimated_minutes": minutes,
                "tags": tags,
                "due_date": None
            }
        except Exception as e:
            raise e
    
    def _local_analysis(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        due_date = self._extract_date(text)
        
        return {
            "summary": text.strip()[:200],
            "priority": self._detect_priority(text_lower),
            "estimated_minutes": self._estimate_time(text),
            "tags": self._extract_tags(text_lower),
            "due_date": due_date
        }
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Извлечение даты из текста"""
        today = date.today()
        text_lower = text.lower()
        
        # Явная дата ДД.ММ.ГГГГ
        match = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', text)
        if match:
            try:
                d, m, y = int(match.group(1)), int(match.group(2)), int(match.group(3))
                return date(y, m, d).isoformat()
            except:
                pass
        
        # Послезавтра (ДО "завтра" чтобы не перехватило)
        if 'послезавтра' in text_lower:
            return (today + timedelta(days=2)).isoformat()
        
        # Завтра
        if 'завтра' in text_lower:
            return (today + timedelta(days=1)).isoformat()
        
        # Сегодня
        if 'сегодня' in text_lower:
            return today.isoformat()
        
        # Через N дней
        match = re.search(r'через\s+(\d+)\s*(?:день|дня|дней)', text_lower)
        if match:
            return (today + timedelta(days=int(match.group(1)))).isoformat()
        
        # Через неделю
        if 'через неделю' in text_lower:
            return (today + timedelta(days=7)).isoformat()
        
        # Дни недели
        days_map = {
            'понедельник': 0, 'вторник': 1, 'среду': 2, 'среда': 2,
            'четверг': 3, 'пятницу': 4, 'пятница': 4,
            'субботу': 5, 'суббота': 5, 'воскресенье': 6,
        }
        
        current_wd = today.weekday()
        
        for day_name, target_wd in days_map.items():
            if day_name in text_lower:
                days_until = target_wd - current_wd
                if days_until <= 0:
                    days_until += 7
                return (today + timedelta(days=days_until)).isoformat()
        
        return None
    
    def _detect_priority(self, text: str) -> str:
        high = ['срочно', 'asap', 'важно', 'критично', 'дедлайн', 'горит', 'немедленно']
        for w in high:
            if w in text:
                return 'high'
        low = ['потом', 'неспешно', 'когда-нибудь', 'не срочно', 'позже']
        for w in low:
            if w in text:
                return 'low'
        return 'medium'
    
    def _estimate_time(self, text: str) -> int:
        text_lower = text.lower()
        
        if match := re.search(r'(\d+)\s*час', text_lower):
            return int(match.group(1)) * 60
        if match := re.search(r'(\d+)\s*мин', text_lower):
            return int(match.group(1))
        
        times = {'совещание': 60, 'встреча': 60, 'созвон': 30, 'звонок': 15,
                 'отчет': 120, 'отчёт': 120, 'презентация': 180,
                 'письмо': 15, 'email': 15, 'баг': 45, 'планерка': 30}
        
        for task, mins in times.items():
            if task in text_lower:
                return mins
        
        return min(len(text.split()) * 3, 480)
    
    def _extract_tags(self, text: str) -> list:
        tags = []
        tag_map = {
            'отчет': ['отчет', 'отчёт', 'документ', 'презентация'],
            'совещание': ['совещание', 'встреча', 'созвон', 'митинг', 'планерка'],
            'разработка': ['разработ', 'код', 'баг', 'фикс', 'деплой'],
            'почта': ['письмо', 'почта', 'email', 'ответить'],
            'звонок': ['звонок', 'позвонить', 'телефон'],
            'финансы': ['оплат', 'счет', 'счёт', 'бюджет', 'деньги'],
            'покупки': ['купить', 'продукты', 'магазин'],
            'здоровье': ['врач', 'больниц', 'анализ', 'лекарств'],
        }
        for tag, keywords in tag_map.items():
            if any(kw in text for kw in keywords):
                tags.append(tag)
        return tags[:5] if tags else ['задача']


ai_service = YandexGPTService()
