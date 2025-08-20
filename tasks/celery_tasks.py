from django.conf import settings
from tasks.models import Task
from celery import shared_task
from openai import OpenAI
from logging import getLogger

SYSTEM_PROMPT = """
You are a (not so) helpful assistant that estimates the time required to complete a task.
Use the title and description to estimate the time required to complete the task.
You can think out loud to help you come up with the estimated time.
The last line of your response should be the estimated time, in minutes or a qualifier for how long the task will take,
without any title, for example:
Could be "5 minutes", "Several hours", "Several days", "More than I'd like", etc.
Do not leave justifications in tha last line, the following is WRONG:
"Since it’s aimed at an ongoing improvement rather than a quick fix, I’d say this will take “Several days” of committed effort and focus."
Be witty or fun.
"""

logger = getLogger()

@shared_task
def update_task_estimated_time(task_id):
    """
    Update the estimated time for a Task, based on Title and Description.
    """
    task = Task.objects.get(id=task_id)
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    content = f"Title: {task.title}\nDescription: {task.description}"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": content}
        ]
    )
    logger.info(response)
    estimated_time = response.choices[0].message.content.split('\n')[-1]
    task.estimated_time = estimated_time
    logger.info(estimated_time)
    task.save()