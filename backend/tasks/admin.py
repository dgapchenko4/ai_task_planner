from django.contrib import admin
from .models import Task, TaskComment, AIAnalysisLog

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'priority', 'status', 'due_date', 'created_at']
    list_filter = ['priority', 'status', 'created_at']
    search_fields = ['title', 'description', 'tags']
    readonly_fields = ['ai_analysis', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'title', 'description', 'short_summary')
        }),
        ('AI Анализ', {
            'fields': ('priority', 'estimated_duration', 'tags', 'ai_analysis')
        }),
        ('Статус и даты', {
            'fields': ('status', 'start_date', 'due_date', 'completed_at')
        }),
    )

@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'created_at']
    list_filter = ['created_at']

@admin.register(AIAnalysisLog)
class AIAnalysisLogAdmin(admin.ModelAdmin):
    list_display = ['task', 'tokens_used', 'created_at']
    readonly_fields = ['task', 'prompt', 'response', 'tokens_used', 'created_at']