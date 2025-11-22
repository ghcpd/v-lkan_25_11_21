#!/usr/bin/env bash
set -euo pipefail
PYTHON=${PYTHON:-python3}
REPORT_DIR=${REPORT_DIR:-reports}
REPORT_FILE=${REPORT_FILE:-$REPORT_DIR/test_report.json}
mkdir -p "$REPORT_DIR"
exec "$PYTHON" -m pytest --json-report --json-report-file="$REPORT_FILE" "$@"
