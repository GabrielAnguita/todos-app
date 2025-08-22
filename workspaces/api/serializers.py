from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Workspace, WorkspaceMember, Invite

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'username', 'email']


class WorkspaceSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    member_count = serializers.IntegerField(read_only=True)
    task_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Workspace
        fields = ['id', 'name', 'owner', 'member_count', 'task_count', 'created_at']


class WorkspaceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ['name']
        extra_kwargs = {
            'name': {'required': True}
        }


class InviteSerializer(serializers.ModelSerializer):
    workspace = WorkspaceSerializer(read_only=True)
    invited_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Invite
        fields = ['id', 'email', 'workspace', 'invited_by', 'created_at']


class InviteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invite
        fields = ['email']
        extra_kwargs = {
            'email': {'required': True}
        }


class WorkspaceMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    workspace = WorkspaceSerializer(read_only=True)
    
    class Meta:
        model = WorkspaceMember
        fields = ['id', 'user', 'workspace', 'role', 'joined_at']