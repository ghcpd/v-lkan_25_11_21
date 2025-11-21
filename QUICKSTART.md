# Quick Reference Guide

## Installation & Setup

### Windows
```cmd
setup.bat
venv\Scripts\activate.bat
```

### Linux/Mac
```bash
bash setup.sh
source venv/bin/activate
```

## Common Commands

### Collect Metrics (30 seconds)
```bash
python main.py --mode collect --duration 30
```

### Collect Once
```bash
python main.py --mode once
```

### Generate Report
```bash
python main.py --mode report
```

### Run Tests
```bash
python run_tests.py
```

### Run Full Demo
```bash
# Windows
run_test.bat

# Linux/Mac
bash run_test.sh
```

## Docker Commands

```bash
# Build
docker build -t metrics-collector .

# Run (60 seconds)
docker run -v $(pwd)/data:/app/data metrics-collector

# Run custom duration
docker run -v $(pwd)/data:/app/data metrics-collector \
  python main.py --mode collect --duration 120
```

## File Locations

- **Metrics**: `data/metrics.jsonl`
- **Reports**: `data/summary.json`
- **Test Results**: `test_reports/test_report_latest.json`
- **Logs**: `metrics_app.log`
- **Config**: `config.json`

## Configuration Quick Edit

```json
{
  "collection_interval": 5,     // Change collection frequency
  "max_file_size_mb": 100,      // Change file rotation size
  "rotate_files": true          // Enable/disable rotation
}
```

## Programmatic Usage

```python
# Collect metrics
from collector import MetricsCollector
collector = MetricsCollector()
metrics = collector.collect_all_metrics()

# Store metrics
from storage import MetricsStorage
storage = MetricsStorage("data", "metrics.jsonl")
storage.write_metric(metrics)

# Generate report
from reporter import MetricsReporter
reporter = MetricsReporter()
reporter.generate_and_save_report("data/metrics.jsonl", "report.json")
```

## Troubleshooting

### Tests failing?
```bash
# Check Python version (need 3.8+)
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Permission errors?
- Ensure `data/` directory is writable
- Run without admin/root (not needed)

### High CPU usage?
- Increase `collection_interval` in config.json
- Reduce collection duration
