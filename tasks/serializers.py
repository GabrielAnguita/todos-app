from rest_framework import serializers
from .models import Task

class TaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'completed', 
            'assigned_user_id', 'due_date', 'estimated_time'
        ]
        extra_kwargs = {
            'completed': {'required': False},
            'assigned_user_id': {'required': False, 'allow_null': True},
            'due_date': {'required': False, 'allow_null': True},
            'estimated_time': {'required': False, 'allow_null': True},
        }