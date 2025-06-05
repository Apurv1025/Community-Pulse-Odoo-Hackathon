import os
import sys
from pathlib import Path

# Add the project root to Python path
proj_path = Path(__file__).parent.parent
sys.path.insert(0, str(proj_path))

print(f"Starting worker with Python path: {sys.path}")
print(f"Working directory: {os.getcwd()}")

# Import the celery app
from backend.celery_app import celery_app

if __name__ == "__main__":
    print("Starting Celery worker...")
    argv = [
        'worker',
        '--loglevel=INFO',
        '--concurrency=2',  # Use 2 worker processes
        '-n', 'event_worker@%h'  # Name the worker
    ]
    celery_app.worker_main(argv)