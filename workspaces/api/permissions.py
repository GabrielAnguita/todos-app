from rest_framework import permissions
from tasks.services import TaskService


class IsWorkspaceOwner(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return obj.owner == request.user


class IsWorkspaceOwnerOrMember(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return TaskService.user_can_access_workspace(request.user, obj)


class CanInviteToWorkspace(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return obj.owner == request.user


class CanManageInvite(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return (obj.email == request.user.email or 
                obj.workspace.owner == request.user)