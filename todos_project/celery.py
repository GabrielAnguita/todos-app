# todos_project/celery.py
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "todos_project.settings")

app = Celery("todos_project")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Optional sanity check task
@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
