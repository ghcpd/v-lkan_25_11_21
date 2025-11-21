#!/usr/bin/env bash
# End-to-end demo: run collector for a few iterations, create report, run tests
set -e
PYTHON=${PYTHON:-python}
OUTDIR=./data
mkdir -p "$OUTDIR"
echo "Running collector for 3 iterations..."
$PYTHON -c "from collector import RepeatedCollector, collect_metrics; from storage import JsonlWriter; w=JsonlWriter('$OUTDIR/metrics.jsonl'); rc=RepeatedCollector(0, w); rc.start(iterations=3); w.close(); print('collected')"
echo "Generating summary..."
$PYTHON -c "from reporter import generate_summary_from_file; import json; s=generate_summary_from_file('$OUTDIR/metrics.jsonl'); print(json.dumps(s, indent=2))"
echo "Running unit tests..."
./run_tests.sh
