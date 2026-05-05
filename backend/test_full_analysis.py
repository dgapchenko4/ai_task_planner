import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from tasks.ai_service import ai_service
import re
from datetime import datetime, time, date, timedelta
from django.utils import timezone

print("=" * 60)
print("ТЕСТ AI АНАЛИЗА + ИЗВЛЕЧЕНИЯ ДАТЫ И ВРЕМЕНИ")
print("=" * 60)

def extract_datetime_from_text(text):
    """Точно такая же логика как в views.py"""
    today = date.today()
    text_lower = text.lower()
    target_date = None
    
    # Сегодня
    if 'сегодня' in text_lower:
        target_date = today
    # Завтра
    elif 'завтра' in text_lower:
        target_date = today + timedelta(days=1)
    # Послезавтра
    elif 'послезавтра' in text_lower:
        target_date = today + timedelta(days=2)
    # Через N дней
    else:
        match = re.search(r'через\s+(\d+)\s*(?:день|дня|дней)', text_lower)
        if match:
            target_date = today + timedelta(days=int(match.group(1)))
    
    # Дни недели
    if not target_date:
        days_map = {
            'понедельник': 0, 'вторник': 1, 'среда': 2, 'среду': 2,
            'четверг': 3, 'пятница': 4, 'пятницу': 4,
            'суббота': 5, 'субботу': 5, 'воскресенье': 6,
        }
        current_wd = today.weekday()
        for day_name, target_wd in days_map.items():
            if day_name in text_lower:
                days_until = target_wd - current_wd
                if days_until <= 0:
                    days_until += 7
                target_date = today + timedelta(days=days_until)
                break
    
    # Конкретная дата ДД.ММ.ГГГГ
    if not target_date:
        match = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', text)
        if match:
            try:
                d, m, y = int(match.group(1)), int(match.group(2)), int(match.group(3))
                target_date = date(y, m, d)
            except:
                pass
    
    if not target_date:
        return None, None
    
    # Определяем время
    hour, minute = 18, 0  # По умолчанию 18:00
    
    # Ищем время: ЧЧ:ММ, ЧЧ.ММ, в ЧЧ:ММ, в ЧЧ часов, в ЧЧ
    time_patterns = [
        (r'в\s+(\d{1,2})[:.](\d{2})', False),  # "в 15:00", "в 15.00"
        (r'(\d{1,2})[:.](\d{2})', False),       # "15:00", "15.00"
        (r'в\s+(\d{1,2})\s*час', True),          # "в 15 часов", "в 3 часа"
    ]
    
    for pattern, hours_only in time_patterns:
        match = re.search(pattern, text_lower)
        if match:
            hour = int(match.group(1))
            if not hours_only:
                minute = int(match.group(2))
            if hour > 23:
                hour = 18
            if minute > 59:
                minute = 0
            break
    
    return target_date, (hour, minute)


test_tasks = [
    "Завтра совещание",
    "Завтра совещание в 15:00",
    "Завтра в 15.00 совещание",
    "Завтра в 9:30 планерка",
    "В пятницу встреча с клиентом",
    "В пятницу в 14:00 встреча",
    "Сегодня в 17:00 созвон",
    "Через 2 дня сдать отчет",
    "Через 3 дня в 10:00 презентация",
    "25.12.2024 дедлайн проекта",
    "Послезавтра в 11:00 врач",
    "Во вторник подготовить отчет",
    "Срочно починить баг",
    "Купить продукты",
]

print(f"\nСегодня: {date.today().strftime('%d.%m.%Y')} ({date.today().strftime('%A')})")
print(f"Текущий день недели: {date.today().weekday()}")
print("-" * 60)

for task in test_tasks:
    print(f"\n📝 Задача: \"{task}\"")
    
    # AI анализ
    analysis = ai_service.analyze_task(task)
    print(f"🤖 AI: priority={analysis.get('priority')}, time={analysis.get('estimated_minutes')}мин, tags={analysis.get('tags')}")
    
    # Извлечение даты
    target_date, target_time = extract_datetime_from_text(task)
    
    if target_date:
        day_name = target_date.strftime('%A')
        date_str = target_date.strftime('%d.%m.%Y')
        
        if target_date == date.today():
            date_label = "СЕГОДНЯ"
        elif target_date == date.today() + timedelta(days=1):
            date_label = "ЗАВТРА"
        else:
            date_label = date_str
        
        if target_time:
            time_str = f"{target_time[0]:02d}:{target_time[1]:02d}"
            print(f"📅 Дата: {date_label} в {time_str}")
        else:
            print(f"📅 Дата: {date_label} (время по умолчанию 18:00)")
    else:
        print(f"📅 Дата: НЕ ОПРЕДЕЛЕНА (задача без срока)")

print("\n" + "=" * 60)
print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
print("=" * 60)
