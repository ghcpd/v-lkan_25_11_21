# System Metrics Framework

Lightweight Python toolkit for continuously collecting local CPU, memory, disk, and network metrics, persisting them as JSONL, and generating time-windowed summary reports. The project is self-contained with automation scripts, Docker support, and pytest coverage.

## Project Layout

- `collector.py` - main daemon for sampling metrics according to `config.json`.
- `storage.py` - JSONL writer with automatic file rotation.
- `reporter.py` - summarises JSONL streams into aggregated JSON reports.
- `config.json` - default configuration (collection interval, file paths, window size).
- `tests/` - pytest suite for collector, storage, and reporter logic.
- `run_metrics.sh` - bootstraps the virtualenv and runs the collector.
- `run_tests.sh` - executes pytest and produces `test_report.json` from the template.
- `run_test.sh` - demonstration script that collects metrics, generates a summary, then runs the tests.
- `setup.sh` - creates the local virtual environment and installs dependencies.
- `requirements.txt`, `Dockerfile`, `test_report_template.json` - reproducibility artifacts.

## Getting Started

```bash
./setup.sh
./run_metrics.sh --duration 30           # collect metrics for 30 seconds
./run_tests.sh                           # run pytest and create test_report.json
./run_test.sh                            # end-to-end demo (collection + summary + tests)
```

The collector writes JSONL data to `output/metrics.jsonl` (overridable with `--output`). Each line contains a structure such as:

```json
{
  "timestamp": 1731462200,
  "cpu": {"total": 35.5, "per_core": [20.0, 50.0, 30.0, 42.0]},
  "memory": {"total": 16384, "used": 8192, "free": 4096, "available": 8192},
  "disk": {"C:": {"total": 512000, "used": 256000, "free": 256000}},
  "network": {"eth0": {"bytes_sent": 1234567, "bytes_recv": 2345678}}
}
```

## Configuration

`config.json` fields:

- `collection_interval` - seconds between samples (default 5).
- `output_path` - JSONL destination for raw metrics.
- `max_file_size_bytes` - rotate file once this limit is reached.
- `summary_output_path` - default location for the JSON summary.
- `summary_window_seconds` - time window for report aggregation.

Override the output path for ad-hoc runs:

```bash
./run_metrics.sh --duration 60 --output /tmp/metrics.jsonl
```

## Reports

Generate summaries from historical data:

```bash
python reporter.py --source output/metrics.jsonl --window 900 --output output/summary.json
```

The report contains average CPU usage, memory trends, and disk/network utilization per device for the requested time window.

## Testing & Reporting

`run_tests.sh` runs `pytest --json-report`, merges the results with `test_report_template.json`, and emits `test_report.json` suitable for CI ingestion. Tests validate:

- Record shape and persistence in `collector.py`.
- Rotation behaviour in `storage.py`.
- Aggregation accuracy in `reporter.py`.

## Container Usage

Build and run inside Docker:

```bash
docker build -t metrics-framework .
docker run --rm -v "$(pwd)/output:/app/output" metrics-framework --duration 60
```

This starts the collector using the baked-in configuration. Attach a volume to persist JSONL output.
