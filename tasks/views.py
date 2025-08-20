from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, RedirectView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import Http404
from django.db import models
from workspaces.models import Workspace, WorkspaceMember
from .models import Task
from .forms import TaskCreateForm
from functools import cached_property


class WorkspaceRedirectView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        user_workspaces = Workspace.objects.filter(
            models.Q(owner=self.request.user) | 
            models.Q(members__user=self.request.user)
        ).distinct()
        
        if not user_workspaces.exists():
            return reverse('create_workspace')
        
        return reverse('task_list', kwargs={'workspace_id': user_workspaces.first().id})


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        workspace = self.get_workspace()
        return Task.objects.filter(workspace=workspace).select_related(
            'assigned_user', 'created_by'
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_workspace = self.get_workspace()
        workspace_members = current_workspace.members.select_related('user').all()
        context.update({
            'workspaces': self.user_workspaces,
            'current_workspace': current_workspace,
            'workspace_members': workspace_members,
            'create_form': TaskCreateForm(),
        })
        return context

    def get_workspace(self):
        workspace = get_object_or_404(self.user_workspaces, id=self.kwargs['workspace_id'])
        return workspace

    @cached_property
    def user_workspaces(self):
        return Workspace.objects.filter(
                models.Q(owner=self.request.user) | 
                models.Q(members__user=self.request.user)
            ).distinct()


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'
    pk_url_kwarg = 'task_id'
    
    def get_queryset(self):
        return Task.objects.select_related('workspace', 'assigned_user', 'created_by')
    
    def get_object(self, queryset=None):
        task = super().get_object(queryset)
        
        # Check permissions
        if not (task.workspace.owner == self.request.user or 
                WorkspaceMember.objects.filter(workspace=task.workspace, user=self.request.user).exists()):
            raise Http404("Task not found")
        
        return task
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workspace_members = self.object.workspace.members.select_related('user').all()
        context['workspace_members'] = workspace_members
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskCreateForm
    
    def get_workspace(self):
        workspace = get_object_or_404(Workspace, id=self.kwargs['workspace_id'])
        
        # Check permissions
        if not (workspace.owner == self.request.user or 
                WorkspaceMember.objects.filter(workspace=workspace, user=self.request.user).exists()):
            raise Http404("Workspace not found")
        
        return workspace
    
    def form_valid(self, form):
        workspace = self.get_workspace()
        form.instance.workspace = workspace
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('task_list', kwargs={'workspace_id': self.kwargs['workspace_id']})


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    pk_url_kwarg = 'task_id'
    
    def get_queryset(self):
        return Task.objects.select_related('workspace', 'assigned_user', 'created_by')
    
    def get_object(self, queryset=None):
        task = super().get_object(queryset)
        
        # Check permissions
        if not (task.workspace.owner == self.request.user or 
                WorkspaceMember.objects.filter(workspace=task.workspace, user=self.request.user).exists()):
            raise Http404("Task not found")
        
        return task
    
    def get_success_url(self):
        return reverse('task_list', kwargs={'workspace_id': self.object.workspace.id})
