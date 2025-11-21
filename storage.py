"""
Storage utilities for writing metric records to JSONL with lightweight rotation.
"""

from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional


class JSONLStorage:
    """Append-only JSONL writer that rotates when the file crosses a byte threshold."""

    def __init__(
        self,
        file_path: str | os.PathLike[str],
        max_bytes: int = 5 * 1024 * 1024,
        timestamp_fn=time.time,
    ) -> None:
        self.path = Path(file_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.max_bytes = max_bytes
        self._lock = threading.Lock()
        self._timestamp_fn = timestamp_fn

    def _should_rotate(self) -> bool:
        return self.path.exists() and self.path.stat().st_size >= self.max_bytes

    def _rotate(self) -> None:
        if not self.path.exists():
            return
        ts = int(self._timestamp_fn())
        rotated = self.path.with_suffix(self.path.suffix + f".{ts}")
        self.path.replace(rotated)

    def write_record(self, record: Dict[str, Any]) -> None:
        line = json.dumps(record, separators=(",", ":"))
        with self._lock:
            if self._should_rotate():
                self._rotate()
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")

    def read_records(self, limit: Optional[int] = None) -> list[Dict[str, Any]]:
        records: list[Dict[str, Any]] = []
        if not self.path.exists():
            return records
        with self.path.open("r", encoding="utf-8") as handle:
            for idx, line in enumerate(handle):
                if limit is not None and idx >= limit:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    # Skip malformed entries but continue reading future data.
                    continue
        return records
