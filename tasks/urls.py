from django.urls import path
from . import views
from .api import views as api_views

urlpatterns = [
    path('', views.WorkspaceRedirectView.as_view(), name='workspace_redirect'),
    path('workspace/<int:workspace_id>/', views.TaskListView.as_view(), name='task_list'),
    path('workspace/<int:workspace_id>/create/', views.TaskCreateView.as_view(), name='create_task'),
    path('tasks/<int:task_id>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:task_id>/delete/', views.TaskDeleteView.as_view(), name='delete_task'),
    
    # API endpoints
    path('api/workspace/<int:workspace_id>/tasks/', api_views.create_task, name='api_create_task'),
    path('api/tasks/<int:task_id>/', api_views.update_task, name='api_update_task'),
    path('api/tasks/<int:task_id>/estimate/', api_views.estimate_task, name='api_estimate_task'),
]