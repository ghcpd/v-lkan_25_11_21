#!/usr/bin/env bash
set -euo pipefail
# Demo script: run unit tests and generate a demo summary report
echo "Running unit tests..."
./metrics_collector/run_tests.sh
echo "Creating demo collection and report..."
./metrics_collector/run_test.sh
echo "All done. Check metrics_collector/data_demo for results and summary.json"
