FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY collector.py .
COPY storage.py .
COPY reporter.py .
COPY main.py .
COPY config.json .

# Create data directory
RUN mkdir -p data

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default command - run continuous collection for 60 seconds
CMD ["python", "main.py", "--mode", "collect", "--duration", "60"]
