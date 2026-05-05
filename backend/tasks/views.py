from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime, time, date, timedelta
import re

from .models import Task, AIAnalysisLog
from .serializers import TaskSerializer
from .ai_service import ai_service

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        qs = Task.objects.filter(user=self.request.user)
        status = self.request.query_params.get('status')
        priority = self.request.query_params.get('priority')
        search = self.request.query_params.get('search')
        if status: qs = qs.filter(status=status)
        if priority: qs = qs.filter(priority=priority)
        if search: qs = qs.filter(title__icontains=search)
        return qs
    
    def perform_create(self, serializer):
        task = serializer.save(user=self.request.user)
        
        try:
            analysis = ai_service.analyze_task(task.title)
            task.short_summary = analysis.get('summary', task.title[:200])
            task.priority = analysis.get('priority', 'medium')
            task.estimated_duration = analysis.get('estimated_minutes')
            task.tags = analysis.get('tags', [])
            task.ai_analysis = analysis
            
            # Обработка даты
            user_date = self.request.data.get('due_date')
            
            if user_date and str(user_date).strip():
                task.due_date = user_date
            else:
                parsed = self._parse_datetime(task.title)
                if parsed:
                    task.due_date = parsed
            
            task.save()
            AIAnalysisLog.objects.create(task=task, prompt=task.title, response=analysis)
            
        except Exception as e:
            print(f"Error: {e}")
            task.save()
    
    def _parse_datetime(self, text: str):
        """Извлечение даты и времени из текста"""
        today = date.today()
        text_lower = text.lower()
        target_date = None
        hour, minute = 18, 0
        
        # Послезавтра (до завтра!)
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
        
        # Дни недели
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
        
        # Явная дата
        if not target_date:
            match = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', text)
            if match:
                try:
                    target_date = date(int(match.group(3)), int(match.group(2)), int(match.group(1)))
                except: pass
        
        if not target_date:
            return None
        
        # Время: ищем "в ЧЧ:ММ" или "в ЧЧ.ММ" или "ЧЧ:ММ"
        time_match = re.search(r'(?:в\s+)?(\d{1,2})[:.](\d{2})', text_lower)
        if time_match:
            h, m = int(time_match.group(1)), int(time_match.group(2))
            if 0 <= h <= 23 and 0 <= m <= 59:
                hour, minute = h, m
        
        dt = datetime.combine(target_date, time(hour, minute))
        return timezone.make_aware(dt)
    
    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        self.get_object().mark_as_completed()
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
    def calendar_data(self, request):
        tasks = self.get_queryset().filter(due_date__isnull=False)
        return Response([{
            'id': str(t.id), 'title': t.short_summary or t.title[:50],
            'start': t.due_date.isoformat(), 'priority': t.priority,
            'color': t.get_priority_color()
        } for t in tasks])
