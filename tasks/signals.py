from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Task
from .celery_tasks import update_task_estimated_time

def broadcast(group: str, type_: str, payload: dict):
    async_to_sync(get_channel_layer().group_send)(
        group,
        {"type": type_, **payload},
    )

@receiver(post_save, sender=Task)
def on_task_saved(sender, instance: Task, created, **kwargs):
    # Minimal task data
    task_data = {
        "id": instance.id,
        "title": instance.title,
        "description": instance.description,
        "completed": instance.completed,
        "workspace_id": instance.workspace_id,
        "assigned_user_id": instance.assigned_user_id,
        "assigned_user_name": instance.assigned_user.username if instance.assigned_user else None,
        "due_date": instance.due_date.isoformat() if instance.due_date else None,
        "estimated_time": instance.estimated_time,
        "updated_at": instance.updated_at.isoformat(),
    }

    event_type = "task_created" if created else "task_updated"
    
    broadcast(f"task_{instance.id}", event_type, {"task": task_data})
    broadcast(f"workspace_{instance.workspace_id}", event_type, {"task": task_data})

    if created:
        update_task_estimated_time.delay(instance.id)

@receiver(post_delete, sender=Task)
def on_task_deleted(sender, instance: Task, **kwargs):
    # Broadcast to workspace room
    broadcast(
        f"workspace_{instance.workspace_id}",
        "task_deleted",
        {"task_id": instance.id, "workspace_id": instance.workspace_id},
    )