#!/usr/bin/env bash
# Demo end-to-end test: run a small collection and generate a summary
set -euo pipefail
OUT_DIR=./data_demo
mkdir -p "$OUT_DIR"
python - <<'PY'
from metrics_collector.storage import JSONLStorage
from metrics_collector.collector import collect_once
s = JSONLStorage(output_dir='data_demo', base_filename='demo.jsonl', max_bytes=1000000)
for i in range(3):
    s.write(collect_once())
s.close()
print('Wrote demo samples to data_demo/demo.jsonl')
PY
python -m metrics_collector.reporter data_demo/demo.jsonl data_demo/summary.json || true
cat data_demo/summary.json || true
