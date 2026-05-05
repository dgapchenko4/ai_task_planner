from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Email')
    avatar = models.URLField(max_length=500, null=True, blank=True, verbose_name='Аватар')
    telegram_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='Telegram ID')
    
    # Настройки уведомлений
    email_notifications = models.BooleanField(default=True, verbose_name='Уведомления на почту')
    morning_summary = models.BooleanField(default=True, verbose_name='Утренняя сводка')
    morning_summary_time = models.TimeField(default='08:00', verbose_name='Время утренней сводки')
    reminder_before_task = models.IntegerField(default=30, verbose_name='Напоминание до задачи (минут)')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email
