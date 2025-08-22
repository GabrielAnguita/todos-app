"""
Service layer for workspace-related business logic.
"""
from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone

from .models import Workspace, WorkspaceMember, Invite

User = get_user_model()


class WorkspaceService:
    """Service class for workspace operations."""
    
    @staticmethod
    def create_workspace(owner, name):
        """Create a new workspace with the owner as the first member."""
        with transaction.atomic():
            workspace = Workspace.objects.create(owner=owner, name=name)
            # Add owner as member
            WorkspaceMember.objects.create(workspace=workspace, user=owner)
        return workspace
    
    @staticmethod
    def get_user_workspaces(user):
        return Workspace.objects.for_user(user).with_full_prefetch()
    
    @staticmethod
    def user_can_access_workspace(user, workspace):
        return (workspace.owner == user or 
                WorkspaceMember.objects.in_workspace(workspace).for_user(user).exists())
    
    @staticmethod
    def user_can_invite_to_workspace(user, workspace):
        return workspace.owner == user
    
    @staticmethod
    def get_workspace_members(workspace, user):
        if not WorkspaceService.user_can_access_workspace(user, workspace):
            raise PermissionDenied("You don't have access to this workspace")
        
        return WorkspaceMember.objects.in_workspace(workspace).with_user_data()


class InviteService:
    """Service class for invitation operations."""
    
    @staticmethod
    def create_invite(workspace, email, invited_by):
        """Create a new invitation to a workspace."""
        # Permission check
        if not WorkspaceService.user_can_invite_to_workspace(invited_by, workspace):
            raise PermissionDenied("You don't have permission to invite users to this workspace")
        
        # Validate email
        if not email or not email.strip():
            raise ValidationError("Email address is required")
        
        email = email.strip().lower()
        
        # Check if user is already a member
        try:
            user = User.objects.get(email=email)
            if WorkspaceMember.objects.filter(workspace=workspace, user=user).exists():
                raise ValidationError(f"{email} is already a member of this workspace")
        except User.DoesNotExist:
            pass  # User doesn't exist, but we can still send invite
        
        # Check for existing pending invitation
        existing_invite = Invite.objects.for_workspace(workspace).for_email(email).pending().first()
        
        if existing_invite:
            raise ValidationError(f"A pending invitation to {email} already exists for this workspace")
        
        # Create new invitation
        with transaction.atomic():
            invite = Invite.objects.create(
                workspace=workspace,
                email=email,
                invited_by=invited_by,
                status='pending'
            )
            
            # TODO: Send email notification
            
        return invite
    
    @staticmethod
    def accept_invite(invite, user):
        """Accept a workspace invitation."""
        # Validate user can accept this invite
        if invite.email != user.email:
            raise PermissionDenied("You can only accept invitations sent to your email address")
        
        if invite.status != 'pending':
            raise ValidationError("This invitation is no longer pending")
        
        with transaction.atomic():
            # Check if user is already a member (race condition protection)
            if WorkspaceMember.objects.filter(workspace=invite.workspace, user=user).exists():
                raise ValidationError(f"You are already a member of {invite.workspace.name}")
            
            # Add user to workspace
            WorkspaceMember.objects.create(workspace=invite.workspace, user=user)
            
            # Mark invite as accepted
            invite.status = 'accepted'
            invite.responded_at = timezone.now()
            invite.save()
            
            # TODO: Send notifications
            
        return invite.workspace
    
    @staticmethod
    def reject_invite(invite, user):
        """Reject a workspace invitation."""
        # Validate user can reject this invite
        if invite.email != user.email:
            raise PermissionDenied("You can only reject invitations sent to your email address")
        
        if invite.status != 'pending':
            raise ValidationError("This invitation is no longer pending")
        
        with transaction.atomic():
            invite.status = 'rejected'
            invite.responded_at = timezone.now()
            invite.save()
            
            # TODO: Send notifications
            
        return invite
    
    @staticmethod
    def get_pending_invites_for_user(user):
        return Invite.objects.for_email(user.email).pending().with_related_data()
    
    @staticmethod
    def get_invite_with_permissions(invite_id, user):
        try:
            invite = Invite.objects.with_related_data().get(id=invite_id)
        except Invite.DoesNotExist:
            raise Invite.DoesNotExist("Invitation not found")
        
        if invite.email != user.email:
            raise PermissionDenied("You can only access invitations sent to your email address")
        
        return invite