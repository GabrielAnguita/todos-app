from django.db import models


class WorkspaceQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(
            models.Q(owner=user) | models.Q(members__user=user)
        ).distinct()
    
    def owned_by(self, user):
        return self.filter(owner=user)
    
    def with_member_counts(self):
        return self.annotate(member_count=models.Count('members'))
    
    def with_task_counts(self):
        return self.annotate(
            task_count=models.Count('tasks'),
            completed_task_count=models.Count(
                'tasks', filter=models.Q(tasks__completed=True)
            )
        )
    
    def with_full_prefetch(self):
        return self.prefetch_related(
            'members__user',
            'tasks__assigned_user'
        ).select_related('owner')


class WorkspaceMemberQuerySet(models.QuerySet):
    def in_workspace(self, workspace):
        return self.filter(workspace=workspace)
    
    def for_user(self, user):
        return self.filter(user=user)
    
    def with_user_data(self):
        return self.select_related('user', 'workspace')


class InviteQuerySet(models.QuerySet):
    def pending(self):
        return self.filter(status='pending')
    
    def accepted(self):
        return self.filter(status='accepted')
    
    def rejected(self):
        return self.filter(status='rejected')
    
    def for_email(self, email):
        return self.filter(email=email)
    
    def for_workspace(self, workspace):
        return self.filter(workspace=workspace)
    
    def sent_by(self, user):
        return self.filter(invited_by=user)
    
    def with_related_data(self):
        return self.select_related('workspace', 'invited_by')