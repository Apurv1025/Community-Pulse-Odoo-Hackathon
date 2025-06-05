from celery.signals import worker_process_init
from backend.utils.db import create_db_and_tables

@worker_process_init.connect
def init_worker(**kwargs):
    """Initialize the database when a worker starts."""
    print("Initializing database tables for Celery worker...")
    create_db_and_tables()