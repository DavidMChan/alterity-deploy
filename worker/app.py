from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from celery_worker import celery_app

app = FastAPI(title="Alterity Worker API")

class JobRequest(BaseModel):
    job_type: str
    payload: Dict[str, Any]

@app.get("/")
def health_check():
    return {"status": "ok", "service": "alterity-worker"}

@app.post("/jobs/dispatch")
def dispatch_job(job: JobRequest):
    """
    Manually dispatch a job for testing or API-driven execution.
    In production, the API might just push to Redis directly,
    but this endpoint allows the API to trigger Celery tasks.
    """
    task_name = f"worker.tasks.{job.job_type.lower()}"

    try:
        # We'll use a generic task router or specific tasks
        # For now, let's assume we map job_type to a task function
        if job.job_type == "RUN_SURVEY":
            task = celery_app.send_task("worker.celery_worker.run_survey_task", args=[job.payload])
        elif job.job_type == "GENERATE_BACKSTORY":
             task = celery_app.send_task("worker.celery_worker.generate_backstory_task", args=[job.payload])
        else:
            raise HTTPException(status_code=400, detail="Unknown job type")

        return {"status": "dispatched", "task_id": task.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
