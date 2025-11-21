#!/usr/bin/env bash
# Run the metrics collector using default config
set -euo pipefail
python -c "from metrics_collector.collector import Collector; from metrics_collector.storage import JSONLStorage; import json, pkgutil, os; cfg_path='metrics_collector/config.json'; cfg=json.load(open(cfg_path)); st=JSONLStorage(output_dir=cfg.get('output_dir','./data'), base_filename=cfg.get('base_filename','metrics.jsonl'), max_bytes=cfg.get('max_bytes',10485760), backup_count=cfg.get('backup_count',5)); Collector(interval=cfg.get('interval',5), writer=st.write).start()"
