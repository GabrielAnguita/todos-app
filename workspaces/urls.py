from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.WorkspaceCreateView.as_view(), name='create_workspace'),
    path('<int:workspace_id>/invite/', views.invite_form, name='invite_form'),
    path('invites/<int:invite_id>/accept/', views.accept_invite, name='accept_invite'),
    path('invites/<int:invite_id>/reject/', views.reject_invite, name='reject_invite'),
]