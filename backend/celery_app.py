"""
celery_app.py — Sets up Celery for background task processing.

When a user uploads a file, we don't want to make them wait while the AI
analyzes it (could take 10-30 seconds). Instead, we:
1. Instantly return a job_id to the frontend
2. Put the analysis task in a Redis queue
3. A Celery worker picks it up and processes it in the background
4. The frontend polls /api/analyze/status/{job_id} until done

To start the worker:
  celery -A celery_app worker --loglevel=info
"""

from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()

# Create the Celery app
# - broker: Redis acts as the message queue (jobs waiting to be processed)
# - backend: Redis also stores the results of completed jobs
celery_app = Celery(
    "astrashield",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=[
        "workers.image_worker",    # Handles deepfake image detection
        "workers.audio_worker",    # Handles voice clone detection
        "workers.document_worker", # Handles document forgery detection
        "workers.scoring_worker",  # Handles final fraud score calculation
    ]
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,     # Lets us track when a task starts (not just queued/done)
    task_acks_late=True,          # Only mark task as done after worker confirms success
    worker_prefetch_multiplier=1, # One task at a time per worker (prevents overload)
)
