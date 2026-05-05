from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, time, date, timedelta
import re

from .models import Task, AIAnalysisLog
from .serializers import TaskSerializer, TaskUpdateSerializer
from .ai_service import ai_service

class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        return TaskSerializer
    
    def get_queryset(self):
        qs = Task.objects.filter(user=self.request.user)
        
        # Фильтры
        status_filter = self.request.query_params.get('status')
        priority_filter = self.request.query_params.get('priority')
        search = self.request.query_params.get('search')
        tag_filter = self.request.query_params.get('tag')  # НОВОЕ: фильтр по тегу
        
        if status_filter:
            qs = qs.filter(status=status_filter)
        if priority_filter:
            qs = qs.filter(priority=priority_filter)
        if search:
            qs = qs.filter(title__icontains=search)
        if tag_filter:
            # Фильтрация по JSON полю tags
            qs = qs.filter(tags__contains=[tag_filter])
        
        return qs
    
    def perform_create(self, serializer):
        task = serializer.save(user=self.request.user)
        self._analyze_task(task)
        
        # Отправляем уведомление на почту
        self._send_email_notification(task, 'created')
    
    def perform_update(self, serializer):
        task = serializer.save()
        if 'title' in serializer.validated_data:
            self._analyze_task(task)
    
    def _analyze_task(self, task):
        """AI анализ задачи"""
        try:
            analysis = ai_service.analyze_task(task.title)
            task.short_summary = analysis.get('summary', task.title[:200])
            task.priority = analysis.get('priority', 'medium')
            task.estimated_duration = analysis.get('estimated_minutes')
            task.tags = analysis.get('tags', [])
            task.ai_analysis = analysis
            
            if not task.due_date:
                parsed = self._parse_datetime(task.title)
                if parsed:
                    task.due_date = parsed
            
            task.save()
            AIAnalysisLog.objects.create(task=task, prompt=task.title, response=analysis)
        except Exception as e:
            print(f"AI error: {e}")
    
    def _send_email_notification(self, task, action):
        """Отправка уведомления на почту"""
        user = self.request.user
        
        # Проверяем настройки
        if not hasattr(user, 'email_notifications') or not user.email_notifications:
            return
        
        if not settings.EMAIL_HOST_USER or settings.EMAIL_HOST_USER == 'your-email@gmail.com':
            print("Email settings not configured")
            return
        
        try:
            if action == 'created':
                subject = f'Новая задача создана: {task.title[:50]}'
                message = f"""
                Здравствуйте, {user.first_name}!
                
                Создана новая задача:
                
                📝 Заголовок: {task.title}
                📋 Краткая суть: {task.short_summary or 'Не определена'}
                🔥 Приоритет: {task.get_priority_display()}
                ⏱ Время выполнения: {task.estimated_duration or 'Не определено'} минут
                🏷 Теги: {', '.join(task.tags) if task.tags else 'Нет'}
                📅 Срок: {task.due_date.strftime('%d.%m.%Y %H:%M') if task.due_date else 'Не задан'}
                
                Войдите в планировщик: http://localhost:3000
                
                С уважением,
                AI Task Planner
                """
                
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
                print(f"Email sent to {user.email}")
        except Exception as e:
            print(f"Email error: {e}")
    
    def _parse_datetime(self, text: str):
        """Извлечение даты и времени из текста"""
        today = date.today()
        text_lower = text.lower()
        target_date = None
        hour, minute = 18, 0
        
        if 'послезавтра' in text_lower:
            target_date = today + timedelta(days=2)
        elif 'завтра' in text_lower:
            target_date = today + timedelta(days=1)
        elif 'сегодня' in text_lower:
            target_date = today
        else:
            match = re.search(r'через\s+(\d+)\s*(?:день|дня|дней)', text_lower)
            if match:
                target_date = today + timedelta(days=int(match.group(1)))
        
        if not target_date:
            days_map = {'понедельник': 0, 'вторник': 1, 'среду': 2, 'среда': 2,
                       'четверг': 3, 'пятницу': 4, 'пятница': 4,
                       'субботу': 5, 'суббота': 5, 'воскресенье': 6}
            cw = today.weekday()
            for dn, tw in days_map.items():
                if dn in text_lower:
                    d = tw - cw
                    if d <= 0: d += 7
                    target_date = today + timedelta(days=d)
                    break
        
        if not target_date:
            match = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', text)
            if match:
                try:
                    target_date = date(int(match.group(3)), int(match.group(2)), int(match.group(1)))
                except: pass
        
        if not target_date:
            return None
        
        time_match = re.search(r'(?:в\s+)?(\d{1,2})[:.](\d{2})', text_lower)
        if time_match:
            h, m = int(time_match.group(1)), int(time_match.group(2))
            if 0 <= h <= 23 and 0 <= m <= 59:
                hour, minute = h, m
        
        dt = datetime.combine(target_date, time(hour, minute))
        return timezone.make_aware(dt)
    
    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        task = self.get_object()
        task.mark_as_completed()
        
        # Уведомление о выполнении
        if task.user.email_notifications:
            try:
                send_mail(
                    subject=f'Задача выполнена: {task.title[:50]}',
                    message=f'Задача "{task.title}" отмечена как выполненная.',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[task.user.email],
                    fail_silently=True,
                )
            except: pass
        
        return Response({'status': 'ok'})
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        tasks = self.get_queryset()
        return Response({
            'total': tasks.count(),
            'completed': tasks.filter(status='completed').count(),
            'in_progress': tasks.filter(status='in_progress').count(),
            'pending': tasks.filter(status='pending').count(),
            'high_priority': tasks.filter(priority='high').count(),
            'medium_priority': tasks.filter(priority='medium').count(),
            'low_priority': tasks.filter(priority='low').count(),
            'overdue': tasks.filter(due_date__lt=timezone.now(), status__in=['pending', 'in_progress']).count(),
        })
    
    @action(detail=False, methods=['get'])
    def tags_list(self, request):
        """Список всех тегов пользователя"""
        tasks = self.get_queryset()
        all_tags = set()
        for task in tasks:
            if task.tags:
                all_tags.update(task.tags)
        return Response(sorted(list(all_tags)))
    
    @action(detail=False, methods=['get'])
    def calendar_data(self, request):
        tasks = self.get_queryset().filter(due_date__isnull=False)
        return Response([{
            'id': str(t.id), 'title': t.short_summary or t.title[:50],
            'start': t.due_date.isoformat(), 'priority': t.priority,
            'color': t.get_priority_color()
        } for t in tasks])
