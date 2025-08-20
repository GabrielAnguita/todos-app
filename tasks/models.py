from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from workspaces.models import WorkspaceMember


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

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
    def can_be_edited_by(self, user):
        return WorkspaceMember.objects.filter(workspace=self.workspace, user=user).exists()        
