from rest_framework import serializers
from .models import Task, TaskComment, AIAnalysisLog

class TaskSerializer(serializers.ModelSerializer):
    """
    Основной сериализатор для задач
    """
    priority_color = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source='user.email', read_only=True)
    display_title = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'short_summary', 'display_title',
            'priority', 'priority_color', 'estimated_duration',
            'tags', 'start_date', 'due_date', 'status',
            'completed_at', 'ai_analysis', 'user_email',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'short_summary', 'priority', 
                           'estimated_duration', 'tags', 'ai_analysis',
                           'user', 'created_at', 'updated_at']
    
    def get_priority_color(self, obj):
        return obj.get_priority_color()
    
    def get_display_title(self, obj):
        return obj.get_display_title()
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        task = Task.objects.create(**validated_data)
        return task

class TaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['title', 'description', 'start_date', 'due_date', 'status']

class TaskCommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = TaskComment
        fields = ['id', 'task', 'user_name', 'text', 'created_at']
        read_only_fields = ['user']

class AIAnalysisLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIAnalysisLog
        fields = ['id', 'task', 'prompt', 'response', 'tokens_used', 'created_at']
