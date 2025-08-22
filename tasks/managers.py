from django.db import models


class TaskQuerySet(models.QuerySet):
    def in_workspace(self, workspace):
        return self.filter(workspace=workspace)
    
    def assigned_to(self, user):
        return self.filter(assigned_user=user)
    
    def created_by(self, user):
        return self.filter(created_by=user)
    
    def pending(self):
        return self.filter(completed=False)
    
    def completed(self):
        return self.filter(completed=True)
    
    def due_soon(self, days=7):
        from django.utils import timezone
        from datetime import timedelta
        cutoff = timezone.now().date() + timedelta(days=days)
        return self.filter(due_date__lte=cutoff, completed=False)
    
    def overdue(self):
        from django.utils import timezone
        return self.filter(due_date__lt=timezone.now().date(), completed=False)
    
    def with_user_data(self):
        return self.select_related('assigned_user', 'created_by', 'workspace')
    
    def with_workspace_data(self):
        return self.select_related('workspace__owner').prefetch_related('workspace__members')
    
    def for_user_access(self, user):
        return self.filter(
            models.Q(workspace__owner=user) | 
            models.Q(workspace__members__user=user)
        ).distinct()
    
    def ordered_by_priority(self):
        return self.order_by(
            models.Case(
                models.When(due_date__isnull=False, then=models.F('due_date')),
                default=models.F('created_at')
            ),
            '-created_at'
        )