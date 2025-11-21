#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"
METRICS_PATH="${ROOT_DIR}/output/metrics.jsonl"
SUMMARY_PATH="${ROOT_DIR}/output/summary.json"
COLLECTION_DURATION="${COLLECTION_DURATION:-10}"

mkdir -p "${ROOT_DIR}/output"

if [ ! -d "${VENV_DIR}" ]; then
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

# shellcheck disable=SC1090
source "${VENV_DIR}/bin/activate"
pip install -r "${ROOT_DIR}/requirements.txt"

echo "Starting metric collection demo for ${COLLECTION_DURATION}s"
python "${ROOT_DIR}/collector.py" --config "${ROOT_DIR}/config.json" --duration "${COLLECTION_DURATION}" --output "${METRICS_PATH}"

echo "Generating summary report at ${SUMMARY_PATH}"
python "${ROOT_DIR}/reporter.py" --source "${METRICS_PATH}" --window 300 --output "${SUMMARY_PATH}"

echo "Running automated tests"
bash "${ROOT_DIR}/run_tests.sh"

echo "Summary written to ${SUMMARY_PATH} and tests captured in test_report.json"
