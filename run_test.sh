#!/usr/bin/env bash
set -euo pipefail
PYTHON=${PYTHON:-python3}
DATA_DIR=${DATA_DIR:-data}
PREFIX=${PREFIX:-metrics}

rm -rf "$DATA_DIR"
mkdir -p "$DATA_DIR"

# Generate a few sample metrics records quickly
$PYTHON - <<PY
import time
from collector import collect_metrics
from storage import MetricsWriter

writer = MetricsWriter(output_dir="${DATA_DIR}", filename_prefix="${PREFIX}", rotation={"type": "time", "when": "S", "interval": 60, "backup_count": 1})
for _ in range(3):
    writer.write(collect_metrics())
    time.sleep(1)
PY

# Produce a summary report
$PYTHON reporter.py --input-dir "$DATA_DIR" --prefix "$PREFIX" --window-minutes 60 --output "$DATA_DIR/summary.json"

# Run automated tests
./run_tests.sh

echo "Demo run complete. Data in $DATA_DIR, summary at $DATA_DIR/summary.json"
