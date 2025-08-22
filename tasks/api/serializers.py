from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Task
from workspaces.models import Workspace

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'username', 'email']


class WorkspaceSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    member_count = serializers.IntegerField(read_only=True)
    task_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Workspace
        fields = ['id', 'name', 'owner', 'member_count', 'task_count', 'created_at']


class TaskListSerializer(serializers.ModelSerializer):
    assigned_user = UserSerializer(read_only=True)
    assigned_user_name = serializers.CharField(source='assigned_user.username', read_only=True)
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'completed', 'due_date',
            'assigned_user', 'assigned_user_name', 'workspace_name',
            'is_overdue', 'created_at', 'updated_at'
        ]
    
    def get_is_overdue(self, obj):
        if not obj.due_date or obj.completed:
            return False
        from django.utils import timezone
        return obj.due_date < timezone.now().date()


class TaskDetailSerializer(serializers.ModelSerializer):
    assigned_user = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    workspace = WorkspaceSerializer(read_only=True)
    is_overdue = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'completed', 'due_date', 'estimated_time',
            'assigned_user', 'created_by', 'workspace', 'is_overdue', 'can_edit',
            'created_at', 'updated_at'
        ]
    
    def get_is_overdue(self, obj):
        if not obj.due_date or obj.completed:
            return False
        from django.utils import timezone
        return obj.due_date < timezone.now().date()
    
    def get_can_edit(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if not user:
            return False
        from ..services import TaskService
        return TaskService.user_can_edit_task(user, obj)


class TaskCreateSerializer(serializers.ModelSerializer):
    assigned_user_id = serializers.PrimaryKeyRelatedField(
        source='assigned_user',
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'due_date', 'estimated_time', 'assigned_user_id'
        ]
        extra_kwargs = {
            'title': {'required': True},
            'description': {'required': False, 'allow_blank': True},
            'due_date': {'required': False, 'allow_null': True},
            'estimated_time': {'required': False, 'allow_null': True, 'allow_blank': True},
        }


class TaskUpdateSerializer(serializers.ModelSerializer):
    assigned_user_id = serializers.PrimaryKeyRelatedField(
        source='assigned_user',
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'completed', 'due_date', 'estimated_time', 'assigned_user_id'
        ]
        extra_kwargs = {
            'title': {'required': False, 'allow_null': True, 'allow_blank': True},
            'description': {'required': False, 'allow_null': True, 'allow_blank': True},
            'completed': {'required': False},
            'estimated_time': {'required': False, 'allow_null': True, 'allow_blank': True},
            'due_date': {'required': False, 'allow_null': True},
        }
    
    def validate_assigned_user_id(self, value):
        if value and hasattr(self, 'instance') and self.instance:
            from ..services import TaskService
            if not TaskService.user_can_access_workspace(value, self.instance.workspace):
                raise serializers.ValidationError("Assigned user must be a workspace member")
        return value