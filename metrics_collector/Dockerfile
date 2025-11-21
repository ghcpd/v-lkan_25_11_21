FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "-c", "from metrics_collector.collector import Collector; import metrics_collector.config as _; Collector(interval=5, writer=None).start()"]
