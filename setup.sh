#!/usr/bin/env bash
PYTHON=${PYTHON:-python}
virtualenv -p "$PYTHON" venv || python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "Environment setup complete. Activate with: source venv/bin/activate"
