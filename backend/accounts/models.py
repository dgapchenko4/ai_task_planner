from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Расширенная модель пользователя
    """
    email = models.EmailField(unique=True, verbose_name='Email')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='Аватар')
    telegram_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='Telegram ID')
    email_notifications = models.BooleanField(default=True, verbose_name='Уведомления на почту')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return self.email