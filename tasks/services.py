"""
Service layer for task-related business logic.
"""
from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError

from workspaces.models import Workspace, WorkspaceMember
from .models import Task
from .celery_tasks import update_task_estimated_time

User = get_user_model()


class TaskService:
    """Service class for task operations."""
    
    @staticmethod
    def get_user_workspaces(user):
        return Workspace.objects.for_user(user)
    
    @staticmethod
    def get_workspace_tasks(workspace, user, include_completed=True):
        if not TaskService.user_can_access_workspace(user, workspace):
            raise PermissionDenied("You don't have access to this workspace")
        queryset = Task.objects.in_workspace(workspace).with_user_data()
        if not include_completed:
            queryset = queryset.pending()
        return queryset
    
    @staticmethod
    def user_can_access_workspace(user, workspace):
        return (workspace.owner == user or 
                WorkspaceMember.objects.in_workspace(workspace).for_user(user).exists())
    
    @staticmethod
    def user_can_edit_task(user, task):
        return TaskService.user_can_access_workspace(user, task.workspace)
    
    @staticmethod
    def create_task(
        workspace,
        created_by,
        title,
        description=None,
        assigned_user=None,
        due_date=None,
        estimated_time=None
    ):
        if not TaskService.user_can_access_workspace(created_by, workspace):
            raise PermissionDenied("You don't have access to this workspace")
        if assigned_user and not TaskService.user_can_access_workspace(assigned_user, workspace):
            raise ValidationError("Assigned user must be a workspace member")
        with transaction.atomic():
            task = Task.objects.create(
                workspace=workspace,
                created_by=created_by,
                title=title,
                description=description,
                assigned_user=assigned_user,
                due_date=due_date,
                estimated_time=estimated_time
            )
        return task
    
    @staticmethod
    def update_task(task, user, **update_data):
        if not TaskService.user_can_edit_task(user, task):
            raise PermissionDenied("You don't have permission to edit this task")
        if 'assigned_user' in update_data:
            assigned_user = update_data['assigned_user']
            if assigned_user and not TaskService.user_can_access_workspace(assigned_user, task.workspace):
                raise ValidationError("Assigned user must be a workspace member")
        for field, value in update_data.items():
            if hasattr(task, field):
                setattr(task, field, value)
        task.save()
        return task
    
    @staticmethod
    def delete_task(task, user):
        if not TaskService.user_can_edit_task(user, task):
            raise PermissionDenied("You don't have permission to delete this task")
        
        with transaction.atomic():
            task.delete()
    
    @staticmethod
    def assign_task(task, user, assigned_user=None):
        return TaskService.update_task(task, user, assigned_user=assigned_user)
    
    @staticmethod
    def toggle_task_completion(task, user):
        new_status = not task.completed
        return TaskService.update_task(task, user, completed=new_status)
    
    @staticmethod
    def estimate_task_time(task, user):
        if not TaskService.user_can_edit_task(user, task):
            raise PermissionDenied("You don't have permission to estimate this task")
        update_task_estimated_time.delay(task.id)
        return {"message": "Task estimation started"}
    
    @staticmethod
    def get_task_with_permissions(task_id, user):
        try:
            task = Task.objects.select_related(
                'workspace', 'assigned_user', 'created_by'
            ).get(id=task_id)
        except Task.DoesNotExist:
            raise Task.DoesNotExist("Task not found")
        
        if not TaskService.user_can_edit_task(user, task):
            raise PermissionDenied("You don't have access to this task")
        
        return task