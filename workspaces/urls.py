from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_workspace, name='create_workspace'),
    path('<int:workspace_id>/invite/', views.invite_form, name='invite_form'),
]