Metrics Collector

This package continuously collects local system metrics and writes them to JSONL files for time-series analysis. Includes optional reporting and automated tests.

Quick start

- Setup environment (Linux / macOS):
  - chmod +x setup.sh && ./setup.sh
- Run collector (uses config.json):
  - chmod +x run_metrics.sh && ./run_metrics.sh

Run tests

- chmod +x run_tests.sh && ./run_tests.sh

Project layout

- collector.py — main metric collection module
- storage.py — JSON/JSONL writing and file rotation
- reporter.py — optional report generation
- config.json — collection interval, output paths
- tests/ — unit and integration test scripts
- run_metrics.sh — script to start collection
- run_tests.sh — run automated tests
- test_report_template.json — template for test results

Credits

Built using psutil for cross-platform metric collection.
