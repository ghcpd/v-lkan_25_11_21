#!/usr/bin/env bash
set -euo pipefail
CONFIG_PATH=${CONFIG_PATH:-config.json}
PYTHON=${PYTHON:-python3}
exec "$PYTHON" collector.py --config "$CONFIG_PATH"
