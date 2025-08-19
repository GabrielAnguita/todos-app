import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.apps import apps


class TaskConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.task_id = self.scope['url_route']['kwargs']['task_id']
        self.room_group_name = f'task_{self.task_id}'
        
        if self.scope["user"] == AnonymousUser():
            await self.close()
            return
            
        has_access = await self.check_task_access()
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
        try:
            task = Task.objects.select_related('workspace').get(id=self.task_id)
            return self.scope["user"].has_perm('workspaces.view_workspace', task.workspace)
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
        try:
            workspace = Workspace.objects.get(id=self.workspace_id)
            return self.scope["user"].has_perm('workspaces.view_workspace', workspace)
        except Workspace.DoesNotExist:
            return False