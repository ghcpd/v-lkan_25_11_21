import types

import pytest

import collector
from storage import JSONLStorage


class DummyPartition:
    def __init__(self, device: str, mountpoint: str) -> None:
        self.device = device
        self.mountpoint = mountpoint


class DummyUsage:
    def __init__(self, total: int, used: int, free: int) -> None:
        self.total = total
        self.used = used
        self.free = free


class DummyNet:
    def __init__(self, sent: int, recv: int) -> None:
        self.bytes_sent = sent
        self.bytes_recv = recv


@pytest.fixture(autouse=True)
def stub_psutil(monkeypatch):
    monkeypatch.setattr(collector.psutil, "cpu_percent", lambda interval=None, percpu=False: [10.0, 20.0])
    vm = types.SimpleNamespace(total=1024, used=512, free=256, available=768)
    monkeypatch.setattr(collector.psutil, "virtual_memory", lambda: vm)
    monkeypatch.setattr(
        collector.psutil,
        "disk_partitions",
        lambda all=False: [DummyPartition("C:", "/c"), DummyPartition("D:", "/d")],
    )
    monkeypatch.setattr(
        collector.psutil,
        "disk_usage",
        lambda mountpoint: DummyUsage(2048, 1024, 1024),
    )
    monkeypatch.setattr(
        collector.psutil,
        "net_io_counters",
        lambda pernic=True: {"eth0": DummyNet(100, 200), "wlan0": DummyNet(300, 400)},
    )
    yield


def test_collect_once_returns_expected_sections(tmp_path):
    storage = JSONLStorage(tmp_path / "metrics.jsonl")
    metric_collector = collector.MetricCollector(storage, interval=1)
    record = metric_collector.collect_once()

    assert set(record.keys()) == {"timestamp", "cpu", "memory", "disk", "network"}
    assert record["cpu"]["total"] == pytest.approx(15.0)
    assert len(record["cpu"]["per_core"]) == 2
    assert record["memory"]["total"] == 1024
    assert "C:" in record["disk"]
    assert "eth0" in record["network"]


def test_run_persists_records(tmp_path):
    storage_path = tmp_path / "metrics.jsonl"
    storage = JSONLStorage(storage_path)
    metric_collector = collector.MetricCollector(storage, interval=0.1)
    metric_collector.run(duration=0.25)

    contents = storage_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(contents) >= 1
