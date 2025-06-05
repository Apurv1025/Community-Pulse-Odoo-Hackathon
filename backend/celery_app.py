from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Celery with explicit app name and Redis broker
celery_app = Celery(
    'backend',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Configure the scheduler to run once per day at 9:00 AM
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Run daily at 9:00 AM to check for events happening tomorrow
    sender.add_periodic_task(
        crontab(hour=9, minute=0),  # 9:00 AM every day
        sender.signature('backend.email_tasks.schedule_event_reminders'),
        name='daily-event-reminders'
    )

# This ensures tasks are registered correctly
celery_app.autodiscover_tasks(['backend.email_tasks'])