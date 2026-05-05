# ai_task_planner
bash
cat > README.md << 'EOF'
# 🤖 AI Task Planner — Умный планировщик задач

Дипломный проект. Веб-приложение для управления задачами с AI-ассистентом на основе Yandex GPT.

## 📋 Функциональность

- 🔐 **Регистрация и авторизация** пользователей (JWT токены)
- 📝 **Создание задач** с автоматическим AI-анализом
- 🤖 **Yandex GPT** определяет:
  - Краткую суть задачи
  - Приоритет (высокий/средний/низкий)
  - Примерное время выполнения
  - Тематику (теги)
- 📅 **Календарь** с цветовой индикацией приоритетов:
  - 🔴 Красный — высокий
  - 🟡 Желтый — средний
  - 🟢 Зеленый — низкий
- 🏷 **Фильтрация задач по тегам**
- ⚙️ **Настройки уведомлений**:
  - Утренняя сводка задач
  - Напоминания о задачах
- 📧 **Email-уведомления** о регистрации и задачах
- 📊 **Дашборд** со статистикой
- ✏️ **Редактирование и удаление** задач

## 🛠 Технологии

### Backend
- **Python 3.12**
- **Django 6.0** + Django REST Framework
- **PostgreSQL 16**
- **Yandex GPT API** (AI-анализ)
- **Simple JWT** (аутентификация)
- **Celery + Redis** (фоновые задачи)
- **SMTP Яндекс** (email-уведомления)

### Frontend
- **HTML5 + CSS3 + JavaScript** (без фреймворков)
- **FullCalendar** (календарь)
- **Адаптивный дизайн**

## 📁 Структура проекта
ai_task_planner/
├── backend/ # Django приложение
│ ├── config/ # Настройки Django
│ │ ├── settings.py
│ │ ├── urls.py
│ │ └── wsgi.py
│ ├── accounts/ # Пользователи
│ │ ├── models.py # CustomUser
│ │ ├── views.py # Регистрация, настройки
│ │ ├── serializers.py
│ │ └── urls.py
│ ├── tasks/ # Задачи
│ │ ├── models.py # Task, AIAnalysisLog
│ │ ├── views.py # CRUD, статистика, календарь
│ │ ├── serializers.py
│ │ ├── ai_service.py # Yandex GPT интеграция
│ │ └── urls.py
│ ├── manage.py
│ ├── requirements.txt
│ └── .env # Переменные окружения
└── frontend/ # Веб-интерфейс
├── index.html # Главная страница
├── styles.css # Стили
└── script.js # Логика приложения

text

## 🚀 Установка и запуск

### 1. Клонирование репозитория
```bash
git clone <url-репозитория>
cd ai_task_planner
2. Настройка базы данных
bash
sudo -u postgres psql
CREATE DATABASE ai_task_planner;
CREATE USER planner_user WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE ai_task_planner TO planner_user;
\q
3. Установка зависимостей
bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

pip install -r requirements.txt
4. Настройка переменных окружения
Создайте файл .env в папке backend/:

env
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=ai_task_planner
DB_USER=planner_user
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
YANDEX_GPT_API_KEY=your-yandex-api-key
YANDEX_GPT_FOLDER_ID=your-yandex-folder-id
EMAIL_HOST_USER=your-email@yandex.ru
EMAIL_HOST_PASSWORD=your-app-password
5. Миграции и запуск
bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
6. Запуск фронтенда (в отдельном терминале)
bash
cd frontend
python3 -m http.server 3000
7. Открыть в браузере
text
http://localhost:3000
📡 API Endpoints
Аутентификация
Метод	URL	Описание
POST	/api/auth/register/	Регистрация
POST	/api/auth/login/	Вход
GET	/api/auth/profile/	Профиль
GET/PUT	/api/auth/notification-settings/	Настройки уведомлений
Задачи
Метод	URL	Описание
GET	/api/tasks/tasks/	Список задач
POST	/api/tasks/tasks/	Создать задачу
PATCH	/api/tasks/tasks/{id}/	Обновить задачу
DELETE	/api/tasks/tasks/{id}/	Удалить задачу
POST	/api/tasks/tasks/{id}/mark_completed/	Отметить выполненной
GET	/api/tasks/tasks/statistics/	Статистика
GET	/api/tasks/tasks/tags_list/	Список тегов
GET	/api/tasks/tasks/calendar_data/	Данные для календаря
📧 Настройка email-уведомлений
Зарегистрируйте почту на Яндексе

Включите IMAP/POP3 в настройках

Создайте пароль приложения: https://id.yandex.ru/security/app-passwords

Укажите данные в .env

🔄 Утренняя сводка и напоминания
Запуск по расписанию (cron каждые 5 минут):

bash
*/5 * * * * cd /path/to/backend && /path/to/venv/bin/python manage.py send_reminders
📸 Скриншоты
(добавьте скриншоты приложения)

📝 Лицензия
Дипломный проект. Все права защищены.

👤 Автор
Гапченко Дмитрий

Email: dgapchenko4@gmail.com

Telegram: @dima_gapchenko

© 2026 AI Task Planner. All rights reserved.
EOF

text

## Файлы созданы! Проверьте:

```bash
ls -la .gitignore README.md
повторить  readme
bash
cd /mnt/c/Users/User/projects/ai_task_planner

cat > README.md << 'EOF'
# 🤖 AI Task Planner — Умный планировщик задач с искусственным интеллектом

**Дипломный проект**  
Разработка планировщика задач с AI-ассистентом на основе Yandex GPT

---

## 📋 Возможности

### 🔐 Авторизация
- Регистрация новых пользователей
- Вход по email и паролю
- JWT токены (access + refresh)
- Защищенные API endpoints

### 📝 Управление задачами
- Создание задач с AI-анализом
- Редактирование и удаление задач
- Отметка о выполнении
- Автоматическое определение даты и времени из текста:
  - "завтра в 15:00" → завтра 15:00
  - "в пятницу" → ближайшая пятница 18:00
  - "через 3 дня" → +3 дня

### 🤖 AI-анализ (Yandex GPT)
При создании задачи AI автоматически определяет:
- **Краткую суть** — сжатое описание задачи
- **Приоритет** — высокий/средний/низкий
- **Время выполнения** — оценка в минутах
- **Теги** — тематика задачи

### 📅 Календарь
- Отображение задач на календаре
- Цветовая индикация приоритетов:
  - 🔴 **Красный** — высокий приоритет
  - 🟡 **Желтый** — средний приоритет
  - 🟢 **Зеленый** — низкий приоритет
- Переключение: месяц/неделя
- Клик по задаче — просмотр и редактирование

### 🏷 Фильтрация по тегам
- Автоматическое извлечение тегов
- Боковая панель со списком тегов
- Клик по тегу — фильтрация задач
- Сброс фильтра

### ⚙️ Настройки уведомлений
- 🌅 **Утренняя сводка** — список задач на день
- ⏰ **Напоминания** — за 5/15/30/60/120 минут до задачи
- 📧 **Email-уведомления** — включение/отключение
- Все настройки сохраняются в профиле

### 📧 Отправка писем
- Приветственное письмо при регистрации
- Утренняя сводка задач
- Напоминания о предстоящих задачах
- Отправка через Яндекс SMTP

### 📊 Дашборд
- Статистика: всего/активных/выполнено/срочных
- Последние 5 задач

---

## 🛠 Технологический стек

### Backend
| Технология | Назначение |
|-----------|------------|
| Python 3.12 | Язык программирования |
| Django 6.0 | Веб-фреймворк |
| Django REST Framework | REST API |
| PostgreSQL 16 | База данных |
| Simple JWT | Аутентификация |
| Yandex GPT API | Искусственный интеллект |
| Celery + Redis | Фоновые задачи |
| django-cors-headers | CORS |
| python-dotenv | Переменные окружения |

### Frontend
| Технология | Назначение |
|-----------|------------|
| HTML5 | Структура |
| CSS3 | Стили (тёмная тема) |
| JavaScript (Vanilla) | Логика |
| FullCalendar 5 | Календарь |

---

## 📁 Структура проекта
ai_task_planner/
│
├── backend/ # Django backend
│ ├── config/ # Настройки проекта
│ │ ├── init.py
│ │ ├── settings.py # Конфигурация Django
│ │ ├── urls.py # Главные URL
│ │ ├── asgi.py
│ │ └── wsgi.py
│ │
│ ├── accounts/ # Приложение пользователей
│ │ ├── init.py
│ │ ├── models.py # CustomUser (расширенная модель)
│ │ ├── serializers.py # Регистрация, профиль, настройки
│ │ ├── views.py # API регистрации и профиля
│ │ ├── urls.py # URL авторизации
│ │ └── admin.py
│ │
│ ├── tasks/ # Приложение задач
│ │ ├── init.py
│ │ ├── models.py # Task, AIAnalysisLog
│ │ ├── serializers.py # TaskSerializer
│ │ ├── views.py # CRUD, статистика, календарь
│ │ ├── ai_service.py # Yandex GPT + локальный анализ
│ │ ├── urls.py # URL задач
│ │ ├── admin.py
│ │ └── management/
│ │ └── commands/
│ │ └── send_reminders.py # Команда отправки уведомлений
│ │
│ ├── media/ # Загруженные файлы
│ ├── manage.py # Django Management
│ ├── requirements.txt # Зависимости Python
│ └── .env # Переменные окружения
│
├── frontend/ # Веб-интерфейс
│ ├── index.html # Главная страница SPA
│ ├── styles.css # Все стили
│ └── script.js # Вся логика
│
├── .gitignore # Исключения Git
└── README.md # Документация

text

---

## 🚀 Быстрый старт

### 1. Требования
- Python 3.10+
- PostgreSQL 14+
- Redis (опционально)
- Git

### 2. Клонирование
```bash
git clone <url>
cd ai_task_planner
3. База данных
bash
sudo -u postgres psql
CREATE DATABASE ai_task_planner;
CREATE USER planner_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE ai_task_planner TO planner_user;
\q
4. Backend
bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Создайте .env файл
nano .env
Пример .env:

env
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=ai_task_planner
DB_USER=planner_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432
YANDEX_GPT_API_KEY=your-api-key
YANDEX_GPT_FOLDER_ID=your-folder-id
EMAIL_HOST=smtp.yandex.ru
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_HOST_USER=your@yandex.ru
EMAIL_HOST_PASSWORD=app-password
bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
5. Frontend
bash
# В новом терминале
cd frontend
python3 -m http.server 3000
6. Открыть
text
http://localhost:3000
📡 API Документация
Аутентификация
text
POST /api/auth/register/    — Регистрация
POST /api/auth/login/       — Вход (получение JWT)
POST /api/auth/token/refresh/ — Обновление токена
GET  /api/auth/profile/     — Профиль пользователя
GET  /api/auth/notification-settings/  — Настройки уведомлений
PUT  /api/auth/notification-settings/  — Обновить настройки
Задачи
text
GET    /api/tasks/tasks/              — Список задач
POST   /api/tasks/tasks/              — Создать задачу
GET    /api/tasks/tasks/{id}/         — Получить задачу
PATCH  /api/tasks/tasks/{id}/         — Обновить задачу
DELETE /api/tasks/tasks/{id}/         — Удалить задачу
POST   /api/tasks/tasks/{id}/mark_completed/ — Отметить выполненной
GET    /api/tasks/tasks/statistics/   — Статистика
GET    /api/tasks/tasks/tags_list/    — Список тегов
GET    /api/tasks/tasks/calendar_data/ — Данные календаря
Фильтрация
text
GET /api/tasks/tasks/?status=pending
GET /api/tasks/tasks/?priority=high
GET /api/tasks/tasks/?tag=совещание
GET /api/tasks/tasks/?search=отчет
📧 Настройка Яндекс Почты
Зайдите в Яндекс Почту

Настройки → Почтовые программы → Включите IMAP

Создайте пароль приложения: https://id.yandex.ru/security/app-passwords

Выберите тип: "Почта"

Скопируйте 16-значный пароль в .env

🔄 Утренняя сводка (Cron)
bash
# Каждые 5 минут
*/5 * * * * cd /path/to/backend && /path/to/venv/bin/python manage.py send_reminders >> /tmp/reminders.log 2>&1
📸 Демонстрация
(добавьте скриншоты приложения после запуска)

Страница входа

Дашборд со статистикой

Список задач с тегами

Календарь с цветами приоритетов

Настройки уведомлений

Письмо в почте

👨‍💻 Автор
Гапченко Дмитрий Андреевич

📧 Email: dgapchenko4@gmail.com

📧 Яндекс: dimitrygapchenko@yandex.ru

💬 Telegram: @dima_gapchenko

📄 Лицензия
Дипломный проект. Разработано в 2026 году.