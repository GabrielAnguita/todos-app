from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django_htmx.http import HttpResponseClientRedirect
from .models import Workspace, WorkspaceMember, Invite


class WorkspaceCreateView(LoginRequiredMixin, CreateView):
    model = Workspace
    fields = ['name']
    template_name = 'workspaces/create_workspace.html'
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        
        # Create workspace membership for the owner
        WorkspaceMember.objects.create(workspace=self.object, user=self.request.user)
        
        if self.request.htmx:
            return HttpResponseClientRedirect(f'/workspace/{self.object.id}/')
        
        return redirect('task_list', workspace_id=self.object.id)
    
    def get_success_url(self):
        return reverse_lazy('task_list', kwargs={'workspace_id': self.object.id})


@login_required
def invite_form(request, workspace_id):
    workspace = get_object_or_404(Workspace, id=workspace_id)
    
    if not (workspace.owner == request.user or 
            WorkspaceMember.objects.filter(workspace=workspace, user=request.user).exists()):
        return HttpResponse('Permission denied', status=403)
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                
                # Check if user is already a member
                try:
                    user = User.objects.get(email=email)
                    if WorkspaceMember.objects.filter(workspace=workspace, user=user).exists():
                        messages.info(request, f"{email} is already a member of this workspace.")
                        return redirect('task_list', workspace_id=workspace_id)
                except User.DoesNotExist:
                    pass  # User doesn't exist, but we can still send invite
                
                # Check for existing pending invitation
                existing_invite = Invite.objects.filter(
                    workspace=workspace,
                    email=email,
                    status='pending'
                ).first()
                
                if existing_invite:
                    messages.info(request, f"A pending invitation to {email} already exists for this workspace.")
                else:
                    # Create new invitation (this will work even if previous invites were rejected)
                    invite = Invite.objects.create(
                        workspace=workspace,
                        email=email,
                        invited_by=request.user,
                        status='pending'
                    )
                    messages.success(request, f"We've invited {email}, if it exists they will receive an invitation.")
                    
            except Exception as e:
                messages.error(request, f"Failed to send invitation to {email}. Please try again.")
            
            # Redirect back to the workspace task list
            return redirect('task_list', workspace_id=workspace_id)
        else:
            messages.error(request, "Email address is required.")
            return redirect('task_list', workspace_id=workspace_id)
    
    return render(request, 'workspaces/invite_form.html', {'workspace': workspace})


@login_required
@require_POST
def accept_invite(request, invite_id):
    invite = get_object_or_404(Invite, id=invite_id)
    
    # Check if the invite is for the current user
    if invite.email != request.user.email:
        messages.error(request, "You can only accept invitations sent to your email address.")
        return redirect('workspace_redirect')
    
    # Check if invite is still pending
    if invite.status != 'pending':
        messages.error(request, "This invitation is no longer pending.")
        return redirect('workspace_redirect')
    
    try:
        # Check if user is already a member
        if WorkspaceMember.objects.filter(workspace=invite.workspace, user=request.user).exists():
            messages.info(request, f"You are already a member of {invite.workspace.name}.")
        else:
            # Add user to workspace
            WorkspaceMember.objects.create(workspace=invite.workspace, user=request.user)
            messages.success(request, f"You have joined {invite.workspace.name}!")
        
        # Mark invite as accepted
        invite.status = 'accepted'
        invite.responded_at = timezone.now()
        invite.save()
        
        # Redirect to the workspace
        return redirect('task_list', workspace_id=invite.workspace.id)
        
    except Exception as e:
        messages.error(request, "Failed to accept invitation. Please try again.")
        return redirect('workspace_redirect')


@login_required
@require_POST
def reject_invite(request, invite_id):
    invite = get_object_or_404(Invite, id=invite_id)
    
    # Check if the invite is for the current user
    if invite.email != request.user.email:
        messages.error(request, "You can only reject invitations sent to your email address.")
        return redirect('workspace_redirect')
    
    # Check if invite is still pending
    if invite.status != 'pending':
        messages.error(request, "This invitation is no longer pending.")
        return redirect('workspace_redirect')
    
    try:
        # Mark invite as rejected
        invite.status = 'rejected'
        invite.responded_at = timezone.now()
        invite.save()
        
        messages.success(request, f"You have declined the invitation to {invite.workspace.name}.")
        return redirect('workspace_redirect')
        
    except Exception as e:
        messages.error(request, "Failed to reject invitation. Please try again.")
        return redirect('workspace_redirect')
