#!/usr/bin/env bash
set -euo pipefail
python -m pip install --upgrade pip
if [ -f metrics_collector/requirements.txt ]; then
  pip install -r metrics_collector/requirements.txt
fi
echo "Top-level setup complete."
