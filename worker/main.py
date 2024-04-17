from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "Worker",
    backend=settings.CELERY_BACKEND_URL,
    broker=settings.CELERY_BROKER_URL,
)

celery_app.conf.beat_schedule = {
    "ten_minute_crontab": {
        "task": "worker.tasks.scheduled_job.ten_minute_crontab",
        "schedule": crontab(minute="*/10"),  # Run every 10 minutes
        "args": (),  # Optional arguments for the task
    },
    # Add more scheduled tasks here...
}

celery_app.autodiscover_tasks(["worker.tasks"])

celery_app.conf.update(
    task_track_started=True,
    CELERY_CONCURRENCY=settings.CELERY_CONCURRENCY,
)
