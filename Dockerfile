# Simple containerized environment for metrics collector
FROM python:3.11-slim

WORKDIR /app

# Install build deps (psutil has wheels for many platforms, but include gcc as fallback)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default data directory
VOLUME ["/app/data"]

ENTRYPOINT ["python", "collector.py", "--config", "/app/config.json"]
