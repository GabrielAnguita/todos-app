from django.db import models
from workspaces.models import Workspace


def workspace_context(request):
    """Add workspace data to all template contexts."""
    if not request.user.is_authenticated:
        return {}
    
    # Get all workspaces the user has access to
    user_workspaces = Workspace.objects.filter(
        models.Q(owner=request.user) | 
        models.Q(members__user=request.user)
    ).distinct()
    
    # Try to get current workspace from URL
    current_workspace = None
    if hasattr(request, 'resolver_match') and request.resolver_match:
        workspace_id = request.resolver_match.kwargs.get('workspace_id')
        task_id = request.resolver_match.kwargs.get('task_id')
        
        if workspace_id:
            try:
                current_workspace = user_workspaces.get(id=workspace_id)
            except Workspace.DoesNotExist:
                pass
        elif task_id:
            # Get workspace from task
            try:
                from tasks.models import Task
                task = Task.objects.select_related('workspace').get(id=task_id)
                if (task.workspace.owner == request.user or 
                    task.workspace.members.filter(user=request.user).exists()):
                    current_workspace = task.workspace
            except Task.DoesNotExist:
                pass
    
    # Get user's pending invites
    user_pending_invites = []
    if request.user.is_authenticated:
        from workspaces.models import Invite
        user_pending_invites = Invite.objects.filter(
            email=request.user.email,
            status='pending'
        ).select_related('workspace', 'invited_by')
    
    return {
        'user_workspaces': user_workspaces,
        'current_workspace': current_workspace,
        'user_pending_invites': user_pending_invites,
    }