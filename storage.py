"""
Storage utilities for writing metrics to JSONL with optional file rotation.
"""
from __future__ import annotations

import json
import os
import threading
import time
import glob
from datetime import datetime
from typing import Any, Dict, Optional


class RotationPolicy:
    """
    Supports simple time-based or size-based rotation, inspired by logging.handlers.

    Config examples:
    {
        "type": "time",
        "when": "D",      # S, M, H, D
        "interval": 1,
        "backup_count": 7
    }
    {
        "type": "size",
        "max_bytes": 5_000_000,
        "backup_count": 5
    }
    """

    def __init__(self, cfg: Dict[str, Any], output_dir: str, prefix: str) -> None:
        self.type = cfg.get("type", "time")
        self.when = cfg.get("when", "D")
        self.interval = int(cfg.get("interval", 1))
        self.backup_count = int(cfg.get("backup_count", 7))
        self.max_bytes = int(cfg.get("max_bytes", 0))
        self.output_dir = output_dir
        self.prefix = prefix

        if self.type not in {"time", "size"}:
            raise ValueError(f"Unsupported rotation type: {self.type}")
        if self.type == "time" and self.when not in {"S", "M", "H", "D"}:
            raise ValueError("when must be one of S, M, H, D")
        if self.type == "size" and self.max_bytes <= 0:
            raise ValueError("max_bytes must be > 0 for size rotation")

    @classmethod
    def from_config(cls, cfg: Optional[Dict[str, Any]], output_dir: str, prefix: str) -> Optional["RotationPolicy"]:
        if not cfg:
            return None
        return cls(cfg, output_dir=output_dir, prefix=prefix)

    # Time-based rotation helpers
    def _period_key(self, now: float) -> str:
        dt = datetime.utcfromtimestamp(now)
        if self.when == "S":
            return dt.strftime("%Y%m%d_%H%M%S")
        if self.when == "M":
            return dt.strftime("%Y%m%d_%H%M")
        if self.when == "H":
            return dt.strftime("%Y%m%d_%H")
        return dt.strftime("%Y%m%d")  # D

    def current_path(self, now: Optional[float] = None) -> str:
        if now is None:
            now = time.time()
        if self.type == "time":
            key = self._period_key(now)
            filename = f"{self.prefix}-{key}.jsonl"
            return os.path.join(self.output_dir, filename)
        else:  # size
            # base file name without suffix
            filename = f"{self.prefix}.jsonl"
            return os.path.join(self.output_dir, filename)

    def cleanup(self) -> None:
        """Remove old rotated files beyond backup_count."""
        if self.backup_count <= 0:
            return
        pattern = os.path.join(self.output_dir, f"{self.prefix}-*.jsonl") if self.type == "time" else os.path.join(self.output_dir, f"{self.prefix}*.jsonl")
        files = sorted(glob.glob(pattern))
        if len(files) <= self.backup_count:
            return
        for f in files[: len(files) - self.backup_count]:
            try:
                os.remove(f)
            except OSError:
                pass

    # Size-based rotation
    def rotate_if_needed(self, path: str, record_len: int) -> str:
        if self.type != "size":
            return path
        if not os.path.exists(path):
            return path
        # note: ensure record_len includes newline
        if os.path.getsize(path) + record_len <= self.max_bytes:
            return path
        # rotate: shift .{i} suffixes
        for i in range(self.backup_count - 1, 0, -1):
            src = f"{path}.{i}"
            dst = f"{path}.{i+1}"
            if os.path.exists(src):
                try:
                    os.replace(src, dst)
                except OSError:
                    pass
        # move current to .1
        try:
            os.replace(path, f"{path}.1")
        except OSError:
            pass
        # cleanup beyond backup_count
        if self.backup_count > 0:
            extra = f"{path}.{self.backup_count+1}"
            if os.path.exists(extra):
                try:
                    os.remove(extra)
                except OSError:
                    pass
        return path


class MetricsWriter:
    """Thread-safe JSONL metrics writer with optional rotation."""

    def __init__(self, output_dir: str, filename_prefix: str = "metrics", rotation: Optional[Dict[str, Any]] = None):
        self.output_dir = output_dir
        self.prefix = filename_prefix
        self.rotation_policy = RotationPolicy.from_config(rotation, output_dir, filename_prefix)
        self._lock = threading.Lock()
        self._current_path: Optional[str] = None

    def write(self, record: Dict[str, Any]) -> str:
        line = json.dumps(record, separators=(",", ":"))
        # newline counts for size rotation
        record_len = len(line.encode("utf-8")) + 1
        now = time.time()
        if self.rotation_policy:
            path = self.rotation_policy.current_path(now)
        else:
            path = os.path.join(self.output_dir, f"{self.prefix}.jsonl")
        os.makedirs(self.output_dir, exist_ok=True)
        with self._lock:
            if self.rotation_policy:
                if self.rotation_policy.type == "time":
                    if self._current_path != path:
                        self._current_path = path
                        self.rotation_policy.cleanup()
                elif self.rotation_policy.type == "size":
                    path = self.rotation_policy.rotate_if_needed(path, record_len)
            # append line
            with open(path, "a", encoding="utf-8") as f:
                f.write(line)
                f.write("\n")
        return path


__all__ = ["MetricsWriter", "RotationPolicy"]
