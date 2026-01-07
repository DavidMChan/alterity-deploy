import os
import time
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# Redis URL should be in env, defaulting to local
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "alterity_worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# --- Tasks ---

@celery_app.task
def run_survey_task(payload: dict):
    """
    Executes a survey run.
    Payload: { 'run_id': 123, 'methodology': '...', ... }
    """
    print(f"[INFO] Starting survey run: {payload}")
    # Simulating work
    time.sleep(2)

    # TODO: Import core logic here to avoid circular imports
    # from modules.runner import execute_run
    # execute_run(payload)

    return {"status": "completed", "run_id": payload.get("run_id")}

@celery_app.task
def generate_backstory_task(payload: dict):
    """
    Generates a backstory.
    """
    print(f"[INFO] Generating backstory: {payload}")
    time.sleep(2)
    return {"status": "generated", "backstory_id": "simulated_id"}
