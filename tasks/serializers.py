from datetime import datetime, time
from django.contrib.auth import get_user_model
from django.db import models as djmodels
from rest_framework import serializers
from .models import Task

User = get_user_model()


class TaskUpdateSerializer(serializers.ModelSerializer):
    """
    Accepts:
      - assigned_user_id: integer or null (maps to Task.assigned_user)
      - due_date: 'YYYY-MM-DD' or null (date-only)
    """

    assigned_user_id = serializers.PrimaryKeyRelatedField(
        source='assigned_user',
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )
    assigned_user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'completed',
            'assigned_user', 'assigned_user_id',
            'due_date', 'estimated_time'
        ]
        extra_kwargs = {
            'title': {'required': False, 'allow_null': True, 'allow_blank': True},
            'description': {'required': False, 'allow_null': True, 'allow_blank': True},
            'completed': {'required': False},
            'estimated_time': {'required': False, 'allow_null': True},
            'due_date': {'required': False, 'allow_null': True},
        }

    def update(self, instance, validated_data):
        """
        - Accept a date for due_date even if the model field is DateTimeField.
        - Everything else uses standard ModelSerializer update.
        """
        # Apply the rest
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
