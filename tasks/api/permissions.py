from rest_framework import permissions
from django.core.exceptions import PermissionDenied

from ..services import TaskService


class CanAccessWorkspace(permissions.BasePermission):
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        workspace_id = view.kwargs.get('workspace_id')
        if not workspace_id:
            return True
        
        from workspaces.models import Workspace
        try:
            workspace = Workspace.objects.get(id=workspace_id)
            return TaskService.user_can_access_workspace(request.user, workspace)
        except Workspace.DoesNotExist:
            return False


class CanEditTask(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return TaskService.user_can_edit_task(request.user, obj)


class IsWorkspaceOwnerOrMember(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        workspace = getattr(obj, 'workspace', obj)
        return TaskService.user_can_access_workspace(request.user, workspace)


class CanManageWorkspace(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        workspace = getattr(obj, 'workspace', obj)
        return workspace.owner == request.user


class CanAcceptInvite(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return obj.email == request.user.email and obj.status == 'pending'