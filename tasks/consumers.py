import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.apps import apps


class TaskConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.task_id = self.scope['url_route']['kwargs']['task_id']
        self.room_group_name = f'task_{self.task_id}'
        
        print(f"TaskConsumer connect: task_id={self.task_id}, user={self.scope['user']}")
        
        if self.scope["user"] == AnonymousUser():
            print("TaskConsumer: Anonymous user, closing connection")
            await self.close()
            return
            
        has_access = await self.check_task_access()
        if not has_access:
            print(f"TaskConsumer: User {self.scope['user']} has no access to task {self.task_id}")
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        print(f"TaskConsumer: User {self.scope['user']} connected to task {self.task_id}")
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def task_updated(self, event):
        await self.send(text_data=json.dumps({
            'type': 'task_updated',
            'task': event.get('task'),
        }))
        
    async def task_created(self, event):
        await self.send(text_data=json.dumps({
            'type': 'task_created',
            'task': event.get('task'),
        }))

    @database_sync_to_async
    def check_task_access(self):
        Task = apps.get_model('tasks', 'Task')
        WorkspaceMember = apps.get_model('workspaces', 'WorkspaceMember')
        try:
            task = Task.objects.select_related('workspace').get(id=self.task_id)
            user = self.scope["user"]
            # Check if user is owner or member of the workspace
            return (task.workspace.owner == user or 
                    WorkspaceMember.objects.filter(workspace=task.workspace, user=user).exists())
        except Task.DoesNotExist:
            return False


class WorkspaceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.workspace_id = self.scope['url_route']['kwargs']['workspace_id']
        self.room_group_name = f'workspace_{self.workspace_id}'
        
        if self.scope["user"] == AnonymousUser():
            await self.close()
            return
            
        has_access = await self.check_workspace_access()
        if not has_access:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def task_created(self, event):
        await self.send(text_data=json.dumps({
            'type': 'task_created',
            'task': event.get('task'),
        }))

    async def task_updated(self, event):
        await self.send(text_data=json.dumps({
            'type': 'task_updated',
            'task': event.get('task'),
        }))

    async def task_deleted(self, event):
        await self.send(text_data=json.dumps({
            'type': 'task_deleted',
            'task_id': event['task_id'],
        }))

    @database_sync_to_async
    def check_workspace_access(self):
        Workspace = apps.get_model('workspaces', 'Workspace')
        WorkspaceMember = apps.get_model('workspaces', 'WorkspaceMember')
        try:
            workspace = Workspace.objects.get(id=self.workspace_id)
            user = self.scope["user"]
            # Check if user is owner or member of the workspace
            return (workspace.owner == user or 
                    WorkspaceMember.objects.filter(workspace=workspace, user=user).exists())
        except Workspace.DoesNotExist:
            return False