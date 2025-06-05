from celery import Celery
import os

# Initialize Celery
celery_app = Celery('backend')

# Configure using Redis (make sure Redis is installed and running)
celery_app.conf.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Auto-discover tasks from all modules
celery_app.autodiscover_tasks(['backend.email_tasks'])