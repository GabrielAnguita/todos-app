from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import PermissionDenied, ValidationError
from django_htmx.http import HttpResponseClientRedirect
from .models import Workspace, WorkspaceMember, Invite
from .services import WorkspaceService, InviteService


class WorkspaceCreateView(LoginRequiredMixin, CreateView):
    model = Workspace
    fields = ['name']
    template_name = 'workspaces/create_workspace.html'
    
    def form_valid(self, form):
        workspace = WorkspaceService.create_workspace(
            owner=self.request.user,
            name=form.cleaned_data['name']
        )
        self.object = workspace
        
        if self.request.htmx:
            return HttpResponseClientRedirect(f'/workspace/{workspace.id}/')
        
        return redirect('task_list', workspace_id=workspace.id)
    
    def get_success_url(self):
        return reverse_lazy('task_list', kwargs={'workspace_id': self.object.id})


@login_required
def invite_form(request, workspace_id):
    user_workspaces = WorkspaceService.get_user_workspaces(request.user)
    workspace = get_object_or_404(user_workspaces, id=workspace_id)
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            try:
                InviteService.create_invite(workspace, email, request.user)
                messages.success(request, f"We've invited {email}, if it exists they will receive an invitation.")
            except (PermissionDenied, ValidationError) as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f"Failed to send invitation to {email}. Please try again.")
            
            return redirect('task_list', workspace_id=workspace_id)
        else:
            messages.error(request, "Email address is required.")
            return redirect('task_list', workspace_id=workspace_id)
    
    return render(request, 'workspaces/invite_form.html', {'workspace': workspace})


@login_required
@require_POST
def accept_invite(request, invite_id):
    try:
        invite = InviteService.get_invite_with_permissions(invite_id, request.user)
        workspace = InviteService.accept_invite(invite, request.user)
        messages.success(request, f"You have joined {workspace.name}!")
        return redirect('task_list', workspace_id=workspace.id)
    except Invite.DoesNotExist:
        messages.error(request, "Invitation not found.")
    except (PermissionDenied, ValidationError) as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, "Failed to accept invitation. Please try again.")
    
    return redirect('workspace_redirect')


@login_required
@require_POST
def reject_invite(request, invite_id):
    try:
        invite = InviteService.get_invite_with_permissions(invite_id, request.user)
        InviteService.reject_invite(invite, request.user)
        messages.success(request, f"You have declined the invitation to {invite.workspace.name}.")
    except Invite.DoesNotExist:
        messages.error(request, "Invitation not found.")
    except (PermissionDenied, ValidationError) as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, "Failed to reject invitation. Please try again.")
    
    return redirect('workspace_redirect')
