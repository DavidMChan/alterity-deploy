# Use a base image with Python 3.10
# For Phase 3 (vLLM), we might want to switch to a nvidia/cuda base image.
# For now, a slim python image is fine for the API/Celery logic.
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port for FastAPI
EXPOSE 8000

# Command to run (overridden by docker-compose usually, but default to API or Worker)
# We default to the Redis worker now as it's the main entrypoint
CMD ["python", "redis_worker.py"]
