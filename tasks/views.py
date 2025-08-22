from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, RedirectView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.contrib import messages

from workspaces.models import Workspace, WorkspaceMember
from workspaces.services import WorkspaceService
from .models import Task
from .forms import TaskCreateForm
from .services import TaskService
from functools import cached_property


class WorkspaceRedirectView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        user_workspaces = WorkspaceService.get_user_workspaces(self.request.user)
        
        if not user_workspaces.exists():
            return reverse('create_workspace')
        
        return reverse('task_list', kwargs={'workspace_id': user_workspaces.first().id})


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        try:
            workspace = self.get_workspace()
            return TaskService.get_workspace_tasks(workspace, self.request.user)
        except PermissionDenied:
            raise Http404("Workspace not found")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_workspace = self.get_workspace()
        try:
            workspace_members = WorkspaceService.get_workspace_members(
                current_workspace, self.request.user
            )
        except PermissionDenied:
            raise Http404("Workspace not found")
            
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
        return WorkspaceService.get_user_workspaces(self.request.user)


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'
    pk_url_kwarg = 'task_id'
    
    def get_queryset(self):
        return Task.objects.with_user_data()
    
    def get_object(self, queryset=None):
        try:
            return TaskService.get_task_with_permissions(
                self.kwargs['task_id'], self.request.user
            )
        except (Task.DoesNotExist, PermissionDenied):
            raise Http404("Task not found")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            workspace_members = WorkspaceService.get_workspace_members(
                self.object.workspace, self.request.user
            )
            context['workspace_members'] = workspace_members
        except PermissionDenied:
            raise Http404("Task not found")
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskCreateForm
    
    def get_workspace(self):
        user_workspaces = WorkspaceService.get_user_workspaces(self.request.user)
        return get_object_or_404(user_workspaces, id=self.kwargs['workspace_id'])
    
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
        return Task.objects.with_user_data()
    
    def get_object(self, queryset=None):
        try:
            return TaskService.get_task_with_permissions(
                self.kwargs['task_id'], self.request.user
            )
        except (Task.DoesNotExist, PermissionDenied):
            raise Http404("Task not found")
    
    def get_success_url(self):
        return reverse('task_list', kwargs={'workspace_id': self.object.workspace.id})
