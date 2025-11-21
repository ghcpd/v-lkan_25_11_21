# System Metrics Collection Framework

A comprehensive Python framework for continuous collection of local system metrics with automated testing, structured JSON/JSONL output, and reporting capabilities.

## Features

- **Real-time Metrics Collection**: CPU, Memory, Disk, and Network metrics
- **Structured Output**: JSONL format for time-series analysis
- **Automated Reporting**: Generate summary reports with statistics
- **Comprehensive Testing**: Full test suite with pytest
- **No Admin Required**: Runs with normal user permissions
- **Configurable**: Easy configuration via JSON
- **Dockerized**: Ready-to-deploy container

## Metrics Collected

### CPU Metrics
- Total CPU usage (%)
- Per-core CPU usage (%)

### Memory Metrics
- Total memory (MB)
- Used memory (MB)
- Free memory (MB)
- Available memory (MB)

### Disk Metrics
Per partition:
- Total space (MB)
- Used space (MB)
- Free space (MB)

### Network Metrics
Per interface:
- Bytes sent
- Bytes received

## Project Structure

```
.
├── collector.py              # Metrics collection module
├── storage.py                # JSONL storage handler
├── reporter.py               # Report generation
├── main.py                   # Main application
├── config.json               # Configuration file
├── requirements.txt          # Python dependencies
├── Dockerfile                # Container definition
├── setup.sh / setup.bat      # Environment setup scripts
├── run_metrics.sh / .bat     # Metrics collection scripts
├── run_test.sh / .bat        # Demo and test scripts
├── run_tests.py              # Test runner with reporting
├── tests/                    # Test suite
│   ├── test_collector.py     # Collector tests
│   ├── test_storage.py       # Storage tests
│   ├── test_reporter.py      # Reporter tests
│   └── test_integration.py   # Integration tests
└── data/                     # Output directory (created at runtime)
```

## Quick Start

### Linux/Mac

```bash
# 1. Setup environment
bash setup.sh

# 2. Activate virtual environment
source venv/bin/activate

# 3. Run demo (includes tests + collection)
bash run_test.sh
```

### Windows

```cmd
REM 1. Setup environment
setup.bat

REM 2. Activate virtual environment
venv\Scripts\activate.bat

REM 3. Run demo (includes tests + collection)
run_test.bat
```

### Docker

```bash
# Build image
docker build -t metrics-collector .

# Run container (collects for 60 seconds)
docker run -v $(pwd)/data:/app/data metrics-collector

# Custom duration
docker run -v $(pwd)/data:/app/data metrics-collector python main.py --mode collect --duration 120
```

## Usage

### Collecting Metrics

**Single Collection:**
```bash
python main.py --mode once
```

**Continuous Collection (30 seconds):**
```bash
python main.py --mode collect --duration 30
```

**Continuous Collection (infinite):**
```bash
python main.py --mode collect
```

### Generating Reports

```bash
# Generate report from collected metrics
python main.py --mode report

# Custom output file
python main.py --mode report --output custom_report.json
```

### Running Tests

```bash
# Run all tests with report generation
python run_tests.py

# Run specific test file
pytest tests/test_collector.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

## Configuration

Edit `config.json` to customize behavior:

```json
{
  "collection_interval": 5,        // Seconds between collections
  "output_directory": "data",      // Output directory
  "metrics_file": "metrics.jsonl", // Metrics filename
  "summary_file": "summary.json",  // Summary report filename
  "log_level": "INFO",             // Logging level
  "max_file_size_mb": 100,         // Max file size before rotation
  "rotate_files": true,            // Enable file rotation
  "metrics": {
    "cpu": true,                   // Enable CPU metrics
    "memory": true,                // Enable memory metrics
    "disk": true,                  // Enable disk metrics
    "network": true                // Enable network metrics
  }
}
```

## Output Format

### JSONL Metrics Record

Each line in `data/metrics.jsonl` is a JSON object:

```json
{
  "timestamp": 1731462200,
  "cpu": {
    "total": 35.5,
    "per_core": [20.0, 50.0, 30.0, 42.0]
  },
  "memory": {
    "total": 16384,
    "used": 8192,
    "free": 4096,
    "available": 8192
  },
  "disk": {
    "C:": {
      "total": 512000,
      "used": 256000,
      "free": 256000
    }
  },
  "network": {
    "eth0": {
      "bytes_sent": 1234567,
      "bytes_recv": 2345678
    }
  }
}
```

### Summary Report

The `data/summary.json` contains aggregated statistics:

```json
{
  "generated_at": 1731462300,
  "time_window": {
    "start": 1731462200,
    "end": 1731462260,
    "duration_seconds": 60,
    "sample_count": 12
  },
  "cpu_analysis": {
    "total": {
      "average": 35.5,
      "median": 34.0,
      "min": 20.0,
      "max": 55.0,
      "samples": 12
    },
    "per_core": {
      "core_0": {
        "average": 30.5,
        "min": 15.0,
        "max": 50.0
      }
    }
  },
  "memory_analysis": {
    "total_mb": 16384,
    "used": {
      "average_mb": 8192.5,
      "min_mb": 7800,
      "max_mb": 8500
    }
  }
}
```

## API Reference

### MetricsCollector

```python
from collector import MetricsCollector

collector = MetricsCollector()

# Collect all metrics
metrics = collector.collect_all_metrics()

# Collect specific metrics
cpu = collector.collect_cpu_metrics()
memory = collector.collect_memory_metrics()
disk = collector.collect_disk_metrics()
network = collector.collect_network_metrics()
```

### MetricsStorage

```python
from storage import MetricsStorage

storage = MetricsStorage(
    output_dir="data",
    metrics_file="metrics.jsonl",
    max_file_size_mb=100,
    rotate_files=True
)

# Write single metric
storage.write_metric(metric_data)

# Write multiple metrics
storage.write_metrics_batch(metrics_list)

# Read metrics
metrics = storage.read_metrics(limit=100)

# Get file info
info = storage.get_file_info()
```

### MetricsReporter

```python
from reporter import MetricsReporter

reporter = MetricsReporter()

# Load metrics from file
metrics = reporter.load_metrics_from_file("data/metrics.jsonl")

# Generate report
report = reporter.generate_summary_report(metrics)

# Save report
reporter.save_report(report, "output/report.json")

# All-in-one
reporter.generate_and_save_report(
    "data/metrics.jsonl",
    "data/summary.json"
)
```

## Testing

The framework includes comprehensive tests:

- **Unit Tests**: Test individual components
- **Integration Tests**: Test complete workflows
- **Data Integrity Tests**: Verify data accuracy
- **Error Handling Tests**: Test robustness

### Test Coverage

- `test_collector.py`: 15 tests for metrics collection
- `test_storage.py`: 12 tests for storage operations
- `test_reporter.py`: 13 tests for report generation
- `test_integration.py`: 9 tests for end-to-end workflows

### Test Report

Tests automatically generate a JSON report in `test_reports/`:

```json
{
  "test_run": {
    "timestamp": "2025-11-21T10:30:00",
    "framework": "pytest",
    "python_version": "3.11.5",
    "total_tests": 49,
    "passed": 49,
    "failed": 0,
    "duration_seconds": 12.5
  },
  "system_info": {
    "os": "Windows",
    "cpu_count": 8,
    "total_memory_mb": 16384
  }
}
```

## Requirements

- Python 3.8 or higher
- psutil 5.9.6
- pytest 7.4.3 (for testing)

## Deployment

### Local Deployment

1. Clone/download the project
2. Run `setup.sh` (Linux/Mac) or `setup.bat` (Windows)
3. Activate virtual environment
4. Run `python main.py --mode collect`

### Docker Deployment

1. Build: `docker build -t metrics-collector .`
2. Run: `docker run -v $(pwd)/data:/app/data metrics-collector`

### Production Considerations

- Set appropriate `collection_interval` (5-60 seconds recommended)
- Enable `rotate_files` to prevent unbounded growth
- Monitor disk space in `output_directory`
- Use systemd/supervisor for continuous operation on Linux
- Use Windows Service for continuous operation on Windows

## Troubleshooting

### Permission Errors

All operations run with normal user permissions. If you encounter permission errors:
- Ensure the output directory is writable
- On Linux, avoid system partitions for disk metrics

### High CPU Usage

- Increase `collection_interval` in config.json
- Disable unnecessary metrics in the config

### Memory Issues

- Enable file rotation: `"rotate_files": true`
- Reduce `max_file_size_mb`
- Regularly archive old metrics files

## License

This project is provided as-is for educational and monitoring purposes.

## Contributing

Contributions welcome! Areas for improvement:
- Additional metrics (GPU, temperature, etc.)
- Database storage backends
- Real-time dashboards
- Alert thresholds
- Cloud export capabilities

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review test outputs in `test_reports/`
3. Check application logs in `metrics_app.log`