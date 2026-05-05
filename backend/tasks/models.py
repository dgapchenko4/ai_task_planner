from django.db import models
from django.conf import settings
import uuid

class Task(models.Model):
    """
    Модель задачи
    """
    PRIORITY_CHOICES = [
        ('high', 'Высокий'),
        ('medium', 'Средний'),
        ('low', 'Низкий'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('in_progress', 'В процессе'),
        ('completed', 'Выполнена'),
        ('cancelled', 'Отменена'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks', verbose_name='Пользователь')
    
    # Основные поля
    title = models.CharField(max_length=500, verbose_name='Заголовок задачи')
    description = models.TextField(blank=True, verbose_name='Полное описание')
    short_summary = models.CharField(max_length=200, blank=True, verbose_name='Краткая суть')
    
    # AI-сгенерированные поля
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name='Приоритет')
    estimated_duration = models.IntegerField(null=True, blank=True, verbose_name='Предполагаемое время (минуты)')
    tags = models.JSONField(default=list, verbose_name='Теги/тематика')
    
    # Временные поля
    start_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата начала')
    due_date = models.DateTimeField(null=True, blank=True, verbose_name='Срок выполнения')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата завершения')
    
    # Статус
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    
    # AI анализ
    ai_analysis = models.JSONField(default=dict, blank=True, verbose_name='AI анализ задачи')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлена')
    
    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'priority']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        # Показываем краткую суть, если есть, иначе заголовок
        if self.short_summary and self.short_summary != 'Задача требует выполнения':
            return f"{self.short_summary[:50]}"
        return f"{self.title[:50]}"
    
    def get_display_title(self):
        """Получить отображаемый заголовок задачи"""
        if self.short_summary and self.short_summary != 'Задача требует выполнения':
            return self.short_summary
        return self.title
    
    def mark_as_completed(self):
        """Отметить задачу как выполненную"""
        from django.utils import timezone
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def get_priority_color(self):
        """Получить цвет приоритета"""
        colors = {
            'high': '#ff4444',
            'medium': '#ffbb33',
            'low': '#00C851'
        }
        return colors.get(self.priority, '#ffffff')

class TaskComment(models.Model):
    """
    Комментарии к задаче
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments', verbose_name='Задача')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    text = models.TextField(verbose_name='Текст комментария')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']

class AIAnalysisLog(models.Model):
    """
    Лог AI-анализа задач
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='ai_logs', verbose_name='Задача')
    prompt = models.TextField(verbose_name='Запрос к AI')
    response = models.JSONField(verbose_name='Ответ AI')
    tokens_used = models.IntegerField(default=0, verbose_name='Использовано токенов')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    
    class Meta:
        verbose_name = 'Лог AI анализа'
        verbose_name_plural = 'Логи AI анализа'
