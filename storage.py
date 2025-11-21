import json
import os
import time
from typing import Optional, Callable, Dict, Any

class JsonlWriter:
    def __init__(self, filename: str, max_size_bytes: int = 5 * 1024 * 1024):
        self.base = filename
        self.max_size = max_size_bytes
        os.makedirs(os.path.dirname(self.base) or ".", exist_ok=True)
        self._open_file()

    def _open_file(self):
        if os.path.exists(self.base) and os.path.getsize(self.base) >= self.max_size:
            # rotate existing
            ts = time.time_ns()
            new_name = f"{self.base}.{ts}"
            # Avoid potential name collision
            while os.path.exists(new_name):
                ts += 1
                new_name = f"{self.base}.{ts}"
            os.rename(self.base, new_name)
        self._f = open(self.base, "a", encoding="utf-8")

    def write(self, record: Dict[str, Any]):
        # Serialize to JSON and write newline
        self._f.write(json.dumps(record, separators=(",", ":")) + "\n")
        self._f.flush()
        if self._f.tell() >= self.max_size:
            self._f.close()
            self._open_file()

    def close(self):
        if not self._f.closed:
            self._f.close()

    def read_all(self):
        # Return all records from current file and rotated ones
        def read_file(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        yield json.loads(line)

        yield from read_file(self.base)
        # include rotated files
        dirname = os.path.dirname(self.base) or "."
        base_name = os.path.basename(self.base)
        for name in os.listdir(dirname):
            if name.startswith(base_name + "."):
                yield from read_file(os.path.join(dirname, name))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
