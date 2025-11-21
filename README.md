# v-lkan_25_11_21

This project collects local system metrics as JSONL, provides an optional summary reporter, and automated tests.

Files:
- collector.py: main metric collection module
- storage.py: JSONL writing and rotation
- reporter.py: summary generation
- config.json: configuration for collector
- tests/: pytest tests
- run_metrics.sh, run_tests.sh, run_test.sh: helper scripts

Usage:
1. Install: ./setup.sh
2. Run collector: ./run_metrics.sh
3. Run tests: ./run_tests.sh