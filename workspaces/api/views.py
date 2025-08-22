from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib import messages

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Workspace, Invite
from ..services import WorkspaceService, InviteService
from .serializers import (
    WorkspaceSerializer, WorkspaceCreateSerializer, InviteSerializer, 
    InviteCreateSerializer, WorkspaceMemberSerializer
)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_workspace(request):
    serializer = WorkspaceCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    workspace = WorkspaceService.create_workspace(
        owner=request.user,
        name=serializer.validated_data['name']
    )
    
    return Response(
        WorkspaceSerializer(workspace, context={'request': request}).data,
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def invite_user(request, workspace_id):
    try:
        user_workspaces = WorkspaceService.get_user_workspaces(request.user)
        workspace = get_object_or_404(user_workspaces, id=workspace_id)
    except:
        return Response({'error': 'Workspace not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = InviteCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    try:
        invite = InviteService.create_invite(
            workspace, 
            serializer.validated_data['email'], 
            request.user
        )
        return Response(
            InviteSerializer(invite, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    except (PermissionDenied, ValidationError) as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {'error': f"Failed to send invitation. Please try again."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_invite(request, invite_id):
    try:
        invite = InviteService.get_invite_with_permissions(invite_id, request.user)
        workspace = InviteService.accept_invite(invite, request.user)
        return Response(
            WorkspaceSerializer(workspace, context={'request': request}).data,
            status=status.HTTP_200_OK
        )
    except Invite.DoesNotExist:
        return Response({'error': 'Invitation not found'}, status=status.HTTP_404_NOT_FOUND)
    except (PermissionDenied, ValidationError) as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {'error': 'Failed to accept invitation. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_invite(request, invite_id):
    try:
        invite = InviteService.get_invite_with_permissions(invite_id, request.user)
        InviteService.reject_invite(invite, request.user)
        return Response({'message': 'Invitation rejected successfully'}, status=status.HTTP_200_OK)
    except Invite.DoesNotExist:
        return Response({'error': 'Invitation not found'}, status=status.HTTP_404_NOT_FOUND)
    except (PermissionDenied, ValidationError) as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {'error': 'Failed to reject invitation. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )