# v-lkan_25_11_21

This workspace contains a Python metrics collector project. See `metrics_collector/` for the implementation, tests and scripts.

Key files and usage:

- `metrics_collector/collector.py` — main collector that samples system metrics using `psutil`.
- `metrics_collector/storage.py` — JSONL writer and rotation.
- `metrics_collector/reporter.py` — summary report generation from JSONL files.
- `metrics_collector/config.json` — default configuration.
- `metrics_collector/tests/` — pytest test cases.
- `metrics_collector/run_metrics.sh` — start collector using config.
- `metrics_collector/run_tests.sh` — run unit tests.

See `metrics_collector/README.md` for more details.