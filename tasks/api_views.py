from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from workspaces.models import Workspace, WorkspaceMember
from .models import Task
from .serializers import TaskUpdateSerializer

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    # Check permissions
    if not (task.workspace.owner == request.user or 
            WorkspaceMember.objects.filter(workspace=task.workspace, user=request.user).exists()):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = TaskUpdateSerializer(task, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)