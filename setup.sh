#!/usr/bin/env bash
set -euo pipefail

PYTHON=${PYTHON:-python3}
VENV_DIR=${VENV_DIR:-.venv}

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "Python interpreter '$PYTHON' not found" >&2
  exit 1
fi

$PYTHON -m venv "$VENV_DIR"
# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

echo "Environment ready. Activate with: source $VENV_DIR/bin/activate"
