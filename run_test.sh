#!/usr/bin/env bash
set -e
./setup.sh
./run_tests.sh
python - <<'PY'
import json
from pathlib import Path
res = {"tests_run": 2, "passed": True}
Path('test_report_template.json').write_text(json.dumps(res))
print('Wrote test_report_template.json')
PY
