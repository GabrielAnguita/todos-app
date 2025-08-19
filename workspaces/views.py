from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django_htmx.http import HttpResponseClientRedirect
from .models import Workspace, WorkspaceMember, Invite


@login_required
@require_POST 
def create_workspace(request):
    name = request.POST.get('name', '').strip()
    if not name:
        return HttpResponse('Name required', status=400)
    
    workspace = Workspace.objects.create(name=name, owner=request.user)
    WorkspaceMember.objects.create(workspace=workspace, user=request.user)
    
    if request.htmx:
        return HttpResponseClientRedirect(f'/workspace/{workspace.id}/')
    return redirect('task_list', workspace_id=workspace.id)


@login_required
def invite_form(request, workspace_id):
    workspace = get_object_or_404(Workspace, id=workspace_id)
    
    if not (workspace.owner == request.user or 
            WorkspaceMember.objects.filter(workspace=workspace, user=request.user).exists()):
        return HttpResponse('Permission denied', status=403)
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            invite, created = Invite.objects.get_or_create(
                workspace=workspace,
                email=email,
                defaults={'invited_by': request.user}
            )
            if request.htmx:
                return render(request, 'workspaces/invite_success.html', {'invite': invite})
        return HttpResponse('Email required', status=400)
    
    return render(request, 'workspaces/invite_form.html', {'workspace': workspace})
