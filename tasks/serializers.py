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

    # Map incoming primary key to the FK field
    assigned_user_id = serializers.PrimaryKeyRelatedField(
        source='assigned_user',
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )

    # Force a date-only API for due_date
    due_date = serializers.DateField(required=False, allow_null=True)

    # If you want the response to include the full assigned_user object, keep it read-only here
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
        }

    def update(self, instance, validated_data):
        """
        - Accept a date for due_date even if the model field is DateTimeField.
        - Everything else uses standard ModelSerializer update.
        """
        # If the model uses DateTimeField for due_date, convert incoming date -> midnight datetime
        model_field = instance._meta.get_field('due_date')
        if isinstance(model_field, djmodels.DateTimeField):
            # Pull the date (if present) and set as datetime at 00:00:00
            date_val = validated_data.pop('due_date', None)
            if date_val is not None:
                instance.due_date = datetime.combine(date_val, time.min)

        # Apply the rest
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
