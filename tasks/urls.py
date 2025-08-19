from django.urls import path
from . import views, api_views

urlpatterns = [
    path('', views.WorkspaceRedirectView.as_view(), name='workspace_redirect'),
    path('workspace/<int:workspace_id>/', views.TaskListView.as_view(), name='task_list'),
    path('workspace/<int:workspace_id>/create/', views.TaskCreateView.as_view(), name='create_task'),
    path('tasks/<int:task_id>/', views.TaskDetailView.as_view(), name='task_detail'),
    
    # API endpoints
    path('api/tasks/<int:task_id>/', api_views.update_task, name='api_update_task'),
]