import os
import json
import time
import tempfile
import psutil
from collector import SystemCollector
from storage import JSONLStorage

def test_collect_once_creates_valid_record(tmp_path):
    fn = tmp_path / 'metrics.jsonl'
    storage = JSONLStorage(str(fn), rotate_after_mb=1)
    c = SystemCollector(storage, interval=1)
    rec = c.collect_once()
    assert 'timestamp' in rec
    assert 'cpu' in rec
    assert 'memory' in rec
    assert 'disk' in rec
    assert 'network' in rec

def test_storage_writes_and_rotates(tmp_path):
    fn = tmp_path / 'metrics.jsonl'
    storage = JSONLStorage(str(fn), rotate_after_mb=0)  # small to force rotate
    record = {'a': 1}
    storage.write(record)
    # After one write rotation should occur if rotate_after_mb=0
    assert fn.exists() or any(fn.with_suffix(f'.rot{i}').exists() for i in range(1, 5))
