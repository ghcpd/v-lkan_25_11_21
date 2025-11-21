import time
import os
import json
import pytest
from collector import collect_metrics, RepeatedCollector
from storage import JsonlWriter

def test_collect_format(monkeypatch):
    # Monkeypatch psutil functions with deterministic values
    class Dummy:
        def __init__(self):
            pass
    import psutil

    monkeypatch.setattr(psutil, 'cpu_percent', lambda interval=None, percpu=False: [10.0, 20.0] if percpu else 15.0)
    class VM:
        total = 16000
        used = 8000
        free = 4000
        available = 10000
    monkeypatch.setattr(psutil, 'virtual_memory', lambda: VM())
    class Part:
        def __init__(self, device, mountpoint):
            self.device = device
            self.mountpoint = mountpoint
    monkeypatch.setattr(psutil, 'disk_partitions', lambda all=False: [Part('C:', '/')])
    class DU:
        total = 512000
        used = 256000
        free = 256000
    monkeypatch.setattr(psutil, 'disk_usage', lambda path: DU())
    monkeypatch.setattr(psutil, 'net_io_counters', lambda pernic=False: {'eth0': type('x', (), {'bytes_sent': 1000, 'bytes_recv': 2000})()})

    rec = collect_metrics()
    assert 'timestamp' in rec
    assert isinstance(rec['cpu']['total'], float)
    assert isinstance(rec['cpu']['per_core'], list)
    assert rec['memory']['total'] == 16000
    assert 'C:' in rec['disk']
    assert 'eth0' in rec['network']

def test_repeated_collector_and_write(tmp_path, monkeypatch):
    # Use a short interval and limited iterations
    calls = []
    def fake_write(record):
        calls.append(record)
    rc = RepeatedCollector(interval=0, writer=type('W', (), {'write': fake_write})())
    rc.start(iterations=3)
    assert len(calls) == 3
