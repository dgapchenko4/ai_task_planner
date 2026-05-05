from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from accounts.models import CustomUser
from tasks.models import Task

class Command(BaseCommand):
    help = 'Отправка уведомлений: утренняя сводка и напоминания о задачах'

    def handle(self, *args, **options):
        now = timezone.now()
        today = now.date()
        current_time = now.time()

        users = CustomUser.objects.filter(email_notifications=True)

        for user in users:
            # Утренняя сводка
            if user.morning_summary and user.morning_summary_time:
                summary_time = user.morning_summary_time
                # Проверяем что текущее время в пределах 5 минут от настроенного
                diff_minutes = abs(
                    (current_time.hour * 60 + current_time.minute) -
                    (summary_time.hour * 60 + summary_time.minute)
                )
                if diff_minutes <= 5:
                    self.send_morning_summary(user)

            # Напоминания о задачах
            reminder_minutes = user.reminder_before_task or 30
            reminder_time = now + timedelta(minutes=reminder_minutes)
            
            tasks = Task.objects.filter(
                user=user,
                status__in=['pending', 'in_progress'],
                due_date__isnull=False,
                due_date__gte=now,
                due_date__lte=reminder_time
            )

            for task in tasks:
                self.send_task_reminder(user, task, reminder_minutes)

    def send_morning_summary(self, user):
        """Утренняя сводка задач"""
        today = timezone.now().date()
        tasks_today = Task.objects.filter(
            user=user,
            due_date__date=today,
            status__in=['pending', 'in_progress']
        )
        tasks_overdue = Task.objects.filter(
            user=user,
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        )
        tasks_high = Task.objects.filter(
            user=user,
            priority='high',
            status__in=['pending', 'in_progress']
        )

        message = f'''🌅 Доброе утро, {user.first_name}!

📊 Сводка на сегодня ({today.strftime('%d.%m.%Y')}):

📅 Задач на сегодня: {tasks_today.count()}
🔥 Срочных задач: {tasks_high.count()}
⚠️ Просрочено: {tasks_overdue.count()}
'''

        if tasks_today.exists():
            message += '\n📋 Задачи на сегодня:\n'
            for t in tasks_today:
                message += f'  • {t.short_summary or t.title[:50]}\n'

        message += '\nВойдите в планировщик: http://localhost:3000'

        try:
            send_mail(
                subject=f'Утренняя сводка задач на {today.strftime("%d.%m.%Y")}',
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=True,
            )
            self.stdout.write(f'Morning summary sent to {user.email}')
        except Exception as e:
            self.stdout.write(f'Error sending to {user.email}: {e}')

    def send_task_reminder(self, user, task, minutes):
        """Напоминание о приближающейся задаче"""
        time_left = task.due_date - timezone.now()
        hours = int(time_left.total_seconds() // 3600)
        mins = int((time_left.total_seconds() % 3600) // 60)

        message = f'''⏰ Напоминание о задаче!

📝 {task.title}
📋 {task.short_summary or ''}
🔥 Приоритет: {task.get_priority_display()}
⏱ Через: {hours} ч {mins} мин
📅 Начало: {task.due_date.strftime('%d.%m.%Y %H:%M')}
'''

        try:
            send_mail(
                subject=f'⏰ Скоро: {task.title[:50]}',
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=True,
            )
            self.stdout.write(f'Reminder sent to {user.email} for task {task.id}')
        except Exception as e:
            self.stdout.write(f'Error: {e}')
