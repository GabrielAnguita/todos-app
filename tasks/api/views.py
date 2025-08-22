from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from workspaces.models import WorkspaceMember
from tasks.models import Task
from .serializers import TaskUpdateSerializer, TaskDetailSerializer, TaskCreateSerializer
from tasks.services import TaskService
from tasks.celery_tasks import update_task_estimated_time

@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def update_task(request, task_id):
    try:
        task = TaskService.get_task_with_permissions(task_id, request.user)
    except (Task.DoesNotExist, PermissionDenied):
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        TaskService.delete_task(task, request.user)
        return Response({'message': 'Task deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    
    # Handle PATCH request
    data = request.data.copy()
    for key in ('assigned_user_id', 'due_date', 'estimated_time', 'description', 'title'):
        if key in data and (data[key] == '' or data[key] is None):
            data[key] = None

    serializer = TaskUpdateSerializer(task, data=data, partial=True, context={'request': request})
    serializer.is_valid(raise_exception=True)
    task = serializer.save()
    return Response(TaskDetailSerializer(task, context={'request': request}).data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task(request, workspace_id):
    from workspaces.services import WorkspaceService
    
    try:
        user_workspaces = WorkspaceService.get_user_workspaces(request.user)
        workspace = get_object_or_404(user_workspaces, id=workspace_id)
    except:
        return Response({'error': 'Workspace not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = TaskCreateSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    
    task = serializer.save(workspace=workspace, created_by=request.user)
    return Response(TaskDetailSerializer(task, context={'request': request}).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def estimate_task(request, task_id):
    try:
        task = TaskService.get_task_with_permissions(task_id, request.user)
        result = TaskService.estimate_task_time(task, request.user)
        return Response(result, status=status.HTTP_200_OK)
    except (Task.DoesNotExist, PermissionDenied):
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)