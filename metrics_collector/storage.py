"""storage.py
Handles JSONL writing and file rotation for collected metrics.
"""
import json
import os
import threading
import time
from typing import Optional, Dict, Any


class JSONLStorage:
    """Append JSON records to a JSONL file with simple rotation.

    Rotation policy:
    - Rotate when current file size exceeds max_bytes
    - Keep up to `backup_count` rotated files
    """

    def __init__(
        self, output_dir: str = "./data", base_filename: str = "metrics.jsonl",
        max_bytes: int = 10 * 1024 * 1024, backup_count: int = 5
    ):
        self.output_dir = os.path.abspath(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        self.base_filename = base_filename
        self.max_bytes = int(max_bytes)
        self.backup_count = int(backup_count)
        self._lock = threading.Lock()
        self._open_file()

    def _open_file(self):
        self.current_path = os.path.join(self.output_dir, self.base_filename)
        self._file = open(self.current_path, "a", encoding="utf-8")

    def _rotate(self):
        self._file.close()
        # shift older files
        for i in range(self.backup_count - 1, 0, -1):
            s = f"{self.current_path}.{i}"
            d = f"{self.current_path}.{i+1}"
            if os.path.exists(s):
                os.replace(s, d)
        # move current to .1
        if os.path.exists(self.current_path):
            os.replace(self.current_path, f"{self.current_path}.1")
        self._open_file()

    def _should_rotate(self) -> bool:
        try:
            self._file.flush()
            size = os.path.getsize(self.current_path)
            return size >= self.max_bytes
        except Exception:
            return False

    def write(self, record: Dict[str, Any]):
        raw = json.dumps(record, default=str, separators=(',', ':'))
        with self._lock:
            self._file.write(raw + "\n")
            self._file.flush()
            if self._should_rotate():
                self._rotate()

    def close(self):
        with self._lock:
            try:
                self._file.flush()
                self._file.close()
            except Exception:
                pass


if __name__ == "__main__":
    # Quick manual smoke test
    s = JSONLStorage(output_dir="./data_test", max_bytes=200, backup_count=3)
    for i in range(50):
        s.write({"timestamp": int(time.time()), "v": i})
    s.close()
