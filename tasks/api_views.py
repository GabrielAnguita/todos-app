from django.shortcuts import get_object_or_404

from rest_framework import status, serializers  # <-- make sure serializers is imported if used below
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from workspaces.models import WorkspaceMember
from tasks.models import Task
from tasks.serializers import TaskUpdateSerializer
from tasks.celery_tasks import update_task_estimated_time

@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if not task.can_be_edited_by(request.user):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'DELETE':
        # Delete the task
        task.delete()
        return Response({'message': 'Task deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    
    # Handle PATCH request
    # Normalize empty strings to null so fields can be cleared
    data = request.data.copy()
    for key in ('assigned_user_id', 'due_date', 'estimated_time', 'description', 'title'):
        if key in data and (data[key] == '' or data[key] is None):
            data[key] = None

    serializer = TaskUpdateSerializer(task, data=data, partial=True)
    serializer.is_valid(raise_exception=True)
    task = serializer.save()
    return Response(TaskUpdateSerializer(task).data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def estimate_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if not task.can_be_edited_by(request.user):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    update_task_estimated_time.delay(task_id)
    return Response({'message': 'Task estimation started'}, status=status.HTTP_200_OK)