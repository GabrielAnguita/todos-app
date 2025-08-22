from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import Task
from workspaces.services import WorkspaceService

User = get_user_model()

def validate_workspace_member(user_id, workspace):
    """Validate that user is a member of the workspace"""
    if not user_id:
        return None
    try:
        user = User.objects.get(id=user_id)
        if not WorkspaceService.user_can_access_workspace(user, workspace):
            raise ValidationError("Selected user is not a member of this workspace.")
        return user
    except User.DoesNotExist:
        raise ValidationError("Selected user does not exist.")

class TaskCreateForm(forms.ModelForm):
    assigned_user_id = forms.IntegerField(required=False)
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_user_id']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter task title...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Enter task description...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.workspace = kwargs.pop('workspace', None)
        super().__init__(*args, **kwargs)
        if self.workspace:
            self.fields['assigned_user_id'].validators = [
                lambda value: validate_workspace_member(value, self.workspace)
            ]