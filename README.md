# Metrics Collector Framework

This project collects local system metrics (CPU, memory, disk, network) and stores them in JSONL files.

Usage
- Install dependencies: `pip install -r requirements.txt` or use `./setup.sh`.
- Configure collection interval in `config.json`.
- Start collector: `./run_metrics.sh` or `python collector.py`.
- Generate a summary: `python reporter.py ./data/metrics.jsonl`.
- Run tests: `./run_tests.sh` or `pytest --json-report --json-report-file=test_report.json`.

Project Layout
- `collector.py`: collect metrics and run continuous collector.
- `storage.py`: JSONL writing, rotation and read helpers.
- `reporter.py`: summary aggregation of collected metrics.
- `config.json`: default configuration.
- `tests/`: pytest tests for collector, storage, and reporter.
- `run_metrics.sh`, `run_tests.sh`, `run_test.sh`, `setup.sh`: helper scripts.

Docker
- Build: `docker build -t metrics .`
- Run: `docker run --rm -v $(pwd)/data:/app/data metrics`

Notes
- The collector runs under normal unprivileged users; it uses `psutil` for metric collection.
- JSONL files are rotated if they exceed the configured `max_size_bytes`.

License
This repository is an example project created for demonstration.
