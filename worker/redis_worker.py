import os
import json
import time
import sys
import redis
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.getcwd())

from modules.runner import execute_run

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

def start_worker():
    print(f"[Worker] Connecting to Redis at {REDIS_URL}...")
    try:
        r = redis.from_url(REDIS_URL)
        print("[Worker] Listening on 'alterity_jobs'...")

        while True:
            # BLPOP blocks until an item is available
            # Returns tuple (list_name, data)
            task = r.blpop("alterity_jobs", timeout=0)

            if task:
                _, data = task
                try:
                    payload = json.loads(data)
                    print(f"[Worker] Received job: {payload}")

                    if payload.get("job_type") == "RUN_SURVEY":
                        execute_run(payload)
                    else:
                        print(f"[Worker] Unknown job type: {payload.get('job_type')}")

                except Exception as e:
                    print(f"[Worker Error] Failed to process task: {e}")

    except KeyboardInterrupt:
        print("[Worker] Stopping...")
    except Exception as e:
        print(f"[Worker Fatal Error] {e}")
        time.sleep(5)
        start_worker()

if __name__ == "__main__":
    start_worker()
