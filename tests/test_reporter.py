import json
import math
import os

from reporter import generate_summary


def _write_jsonl(path, records):
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r))
            f.write("\n")


def test_generate_summary(tmp_path):
    records = [
        {
            "timestamp": 1000,
            "cpu": {"total": 10.0, "per_core": [10.0, 10.0]},
            "memory": {"percent": 40.0},
            "disk": {"/dev/sda1": {"percent": 50.0}},
            "network": {"eth0": {"bytes_sent": 100, "bytes_recv": 200}},
        },
        {
            "timestamp": 1005,
            "cpu": {"total": 30.0, "per_core": [20.0, 40.0]},
            "memory": {"percent": 60.0},
            "disk": {"/dev/sda1": {"percent": 55.0}},
            "network": {"eth0": {"bytes_sent": 200, "bytes_recv": 500}},
        },
    ]
    path = tmp_path / "metrics.jsonl"
    _write_jsonl(path, records)

    summary = generate_summary(str(tmp_path), prefix="metrics", window_minutes=None, now=1005)

    assert summary["samples"] == 2
    assert math.isclose(summary["cpu"]["avg_total"], 20.0, rel_tol=1e-6)
    assert summary["cpu"]["per_core_avg"] == [15.0, 25.0]
    assert summary["memory"]["percent"]["min"] == 40.0
    assert summary["memory"]["percent"]["max"] == 60.0
    assert summary["disk"]["/dev/sda1"]["percent_avg"] == 52.5

    net = summary["network"]["eth0"]
    assert net["bytes_sent_delta"] == 100
    assert net["bytes_recv_delta"] == 300
    # elapsed = 5 seconds
    assert math.isclose(net["bytes_sent_per_sec"], 20.0, rel_tol=1e-6)
    assert math.isclose(net["bytes_recv_per_sec"], 60.0, rel_tol=1e-6)
