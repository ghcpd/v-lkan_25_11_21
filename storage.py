import os
import json
from pathlib import Path
from typing import Any

class JSONLStorage:
    def __init__(self, file_path: str, rotate_after_mb: int = 10):
        self.file_path = Path(file_path)
        self.rotate_after_mb = rotate_after_mb
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def _rotate_if_needed(self):
        if not self.file_path.exists():
            return
        size_mb = self.file_path.stat().st_size / (1024 * 1024)
        if size_mb >= self.rotate_after_mb:
            i = 1
            while True:
                candidate = self.file_path.with_suffix(f".rot{i}")
                if not candidate.exists():
                    self.file_path.rename(candidate)
                    break
                i += 1

    def write(self, record: Any):
        self._rotate_if_needed()
        with self.file_path.open('a', encoding='utf-8') as fh:
            fh.write(json.dumps(record, default=str) + "\n")
