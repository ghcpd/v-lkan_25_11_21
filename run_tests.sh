#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"
REPORT_PATH="${ROOT_DIR}/pytest-report.json"
FINAL_REPORT="${ROOT_DIR}/test_report.json"

if [ ! -d "${VENV_DIR}" ]; then
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

# shellcheck disable=SC1090
source "${VENV_DIR}/bin/activate"
pip install -r "${ROOT_DIR}/requirements.txt"

pytest --json-report --json-report-file "${REPORT_PATH}"

python <<'PY'
import json
from pathlib import Path

root = Path(__file__).resolve().parent
template = json.loads(root.joinpath("test_report_template.json").read_text(encoding="utf-8"))
pytest_report = json.loads(root.joinpath("pytest-report.json").read_text(encoding="utf-8"))

summary = pytest_report.get("summary", {})
template["summary"].update(
    {
        "total": summary.get("total", 0),
        "passed": summary.get("passed", 0),
        "failed": summary.get("failed", 0),
        "skipped": summary.get("skipped", 0),
    }
)
template["tests"] = pytest_report.get("tests", [])

root.joinpath("test_report.json").write_text(json.dumps(template, indent=2), encoding="utf-8")
print("Wrote test_report.json")
PY
echo "Test results written to ${FINAL_REPORT}"
