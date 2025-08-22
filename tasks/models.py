from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from workspaces.models import WorkspaceMember
from .managers import TaskQuerySet


class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    workspace = models.ForeignKey('workspaces.Workspace', on_delete=models.CASCADE, related_name='tasks')
    assigned_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_tasks')
    due_date = models.DateField(null=True, blank=True)
    estimated_time = models.CharField(max_length=200, null=True, blank=True, help_text="Estimated time")
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TaskQuerySet.as_manager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
    def can_be_edited_by(self, user):
        return WorkspaceMember.objects.filter(workspace=self.workspace, user=user).exists()
    
    def assign_to(self, user):
        if user and not self.can_be_edited_by(user):
            raise ValidationError("Assigned user must be a workspace member")
        self.assigned_user = user
        self.save(update_fields=['assigned_user'])
    
    def mark_completed(self):
        self.completed = True
        self.save(update_fields=['completed'])
    
    def mark_incomplete(self):
        self.completed = False
        self.save(update_fields=['completed'])
