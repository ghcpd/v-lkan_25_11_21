#!/usr/bin/env bash
PYTHON=${PYTHON:-python}
pytest --json-report --json-report-file=test_report.json
echo "Test report written to test_report.json"
