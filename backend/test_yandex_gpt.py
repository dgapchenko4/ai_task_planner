import os
import json
import requests

# Настройки из .env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.conf import settings

API_KEY = settings.YANDEX_GPT_API_KEY
FOLDER_ID = settings.YANDEX_GPT_FOLDER_ID

print(f"API Key: {API_KEY[:10]}..." if API_KEY else "API Key: НЕ НАСТРОЕН")
print(f"Folder ID: {FOLDER_ID}")
print("-" * 50)

def test_task(task_text):
    """Тестируем AI на конкретной задаче"""
    print(f"\n📝 Задача: {task_text}")
    
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {API_KEY}"
    }
    
    prompt = f"""Проанализируй задачу и верни ТОЛЬКО JSON без пояснений:

Задача: {task_text}

Формат ответа:
{{
    "summary": "краткая суть",
    "priority": "high/medium/low",
    "estimated_minutes": число,
    "tags": ["тег1", "тег2"]
}}

Правила:
- priority: high если срочно/важно/дедлайн/ASAP
- estimated_minutes: примерное время в минутах (15, 30, 60, 120 и т.д.)
- tags: 1-3 ключевых слова"""

    body = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.3,
            "maxTokens": "500"
        },
        "messages": [
            {
                "role": "system",
                "text": "Ты — ассистент для анализа задач. Отвечай строго JSON."
            },
            {
                "role": "user",
                "text": prompt
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=body, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            text = data['result']['alternatives'][0]['message']['text']
            print(f"✅ Ответ AI: {text}")
            
            # Парсим JSON
            try:
                clean = text.strip()
                for prefix in ['```json', '```']:
                    if clean.startswith(prefix):
                        clean = clean[len(prefix):]
                if clean.endswith('```'):
                    clean = clean[:-3]
                result = json.loads(clean.strip())
                print(f"📊 Разбор:")
                print(f"   Суть: {result.get('summary')}")
                print(f"   Приоритет: {result.get('priority')}")
                print(f"   Время: {result.get('estimated_minutes')} мин")
                print(f"   Теги: {result.get('tags')}")
            except Exception as e:
                print(f"⚠️ Ошибка парсинга JSON: {e}")
        else:
            print(f"❌ Ошибка API: {response.status_code}")
            print(f"   {response.text}")
    except Exception as e:
        print(f"❌ Ошибка соединения: {e}")

# Тестируем разные задачи
test_cases = [
    "Завтра совещание",
    "Завтра совещание в 12:00",
    "В пятницу встреча с клиентом",
    "Подготовить отчет за квартал",
    "Срочно починить баг в продакшене",
    "Позвонить маме",
    "Купить продукты на неделю",
    "Через 2 дня сдать проект",
]

for task in test_cases:
    test_task(task)

print("\n" + "=" * 50)
print("Тестирование завершено!")
