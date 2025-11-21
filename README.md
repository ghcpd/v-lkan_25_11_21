# System Metrics Collector

Continuously collect local system metrics (CPU, memory, disk, network) and write them to JSONL for time-series analysis. Includes optional summary reporting and automated tests to validate functionality and data integrity.

## Features
- CPU: total and per-core utilization
- Memory: total, used, free, available, percent
- Disk: per-partition total/used/free/percent
- Network: per-interface bytes/packets (cumulative)
- Configurable collection interval
- JSONL output with optional file rotation (time/size)
- Summary reporter (averages, deltas)
- Pytest suite with JSON report output

## Quickstart
```bash
./setup.sh             # create venv and install deps
./run_metrics.sh       # start collector (uses config.json)
./run_tests.sh         # run automated tests
./run_test.sh          # demo: collect a few samples, summarize, run tests
```

### Docker
```bash
docker build -t metrics-collector .
docker run --rm -v $(pwd)/data:/app/data metrics-collector
```

## Configuration (`config.json`)
```json
{
	"collection_interval_seconds": 5,
	"output_dir": "data",
	"metrics_filename_prefix": "metrics",
	"rotation": {
		"type": "time",    // "time" or "size"
		"when": "D",        // S, M, H, D (time-based)
		"interval": 1,
		"backup_count": 7
	},
	"summary": {
		"enabled": false,
		"output_path": "data/summary.json",
		"window_minutes": 60
	}
}
```

## Data Schema (JSONL record)
```json
{
	"timestamp": 1731462200,
	"cpu": {"total": 35.5, "per_core": [20.0, 50.0, 30.0, 42.0]},
	"memory": {"total": 16384, "used": 8192, "free": 4096, "available": 8192, "percent": 50.0},
	"disk": {"C:": {"total": 512000, "used": 256000, "free": 256000, "percent": 50.0}},
	"network": {"eth0": {"bytes_sent": 1234567, "bytes_recv": 2345678, "packets_sent": 0, "packets_recv": 0, "errin": 0, "errout": 0, "dropin": 0, "dropout": 0}}
}
```

Notes:
- Memory and disk values are in **bytes**; percent fields are 0-100.
- Network counters are cumulative; reporter computes deltas and rates per second.

## Reporter
Generate summary JSON from collected metrics:
```bash
python reporter.py --input-dir data --prefix metrics --window-minutes 60 --output data/summary.json
```
Outputs average CPU (total/per-core), memory percent (avg/min/max), disk percent avg per device, and network byte deltas/rates.

## Project Structure
- `collector.py` — metric collection loop
- `storage.py` — JSONL writer with rotation
- `reporter.py` — summary aggregation
- `config.json` — configuration
- `tests/` — pytest suite
- `run_metrics.sh` — start collector
- `run_tests.sh` — run tests (JSON report)
- `run_test.sh` — demo end-to-end
- `setup.sh` — local env setup
- `requirements.txt` — dependencies
- `Dockerfile` — containerized runner
- `test_report_template.json` — test report schema

## Testing
```bash
./run_tests.sh
```
Generates `reports/test_report.json` (via `pytest-json-report`).

## License
MIT (adjust as needed).