from django.urls import path
from . import views
from .api import views as api_views

urlpatterns = [
    path('create/', views.WorkspaceCreateView.as_view(), name='create_workspace'),
    path('<int:workspace_id>/invite/', views.invite_form, name='invite_form'),
    path('invites/<int:invite_id>/accept/', views.accept_invite, name='accept_invite'),
    path('invites/<int:invite_id>/reject/', views.reject_invite, name='reject_invite'),
    
    # API endpoints
    path('api/workspaces/', api_views.create_workspace, name='api_create_workspace'),
    path('api/workspaces/<int:workspace_id>/invite/', api_views.invite_user, name='api_invite_user'),
    path('api/invites/<int:invite_id>/accept/', api_views.accept_invite, name='api_accept_invite'),
    path('api/invites/<int:invite_id>/reject/', api_views.reject_invite, name='api_reject_invite'),
]