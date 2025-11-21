import json
import time

from reporter import MetricReporter


def test_generate_summary_returns_averages(tmp_path):
    metrics_path = tmp_path / "metrics.jsonl"
    now = int(time.time())
    records = [
        {
            "timestamp": now - 2,
            "cpu": {"total": 10.0, "per_core": [10.0, 10.0]},
            "memory": {"total": 100, "used": 30, "free": 70, "available": 80},
            "disk": {"disk0": {"total": 1000, "used": 400, "free": 600}},
            "network": {"eth0": {"bytes_sent": 100, "bytes_recv": 200}},
        },
        {
            "timestamp": now - 1,
            "cpu": {"total": 30.0, "per_core": [20.0, 40.0]},
            "memory": {"total": 100, "used": 50, "free": 50, "available": 60},
            "disk": {"disk0": {"total": 1000, "used": 500, "free": 500}},
            "network": {"eth0": {"bytes_sent": 200, "bytes_recv": 400}},
        },
    ]
    with metrics_path.open("w", encoding="utf-8") as handle:
        for rec in records:
            handle.write(json.dumps(rec) + "\n")

    reporter = MetricReporter(metrics_path, window_seconds=60)
    summary = reporter.generate_summary()

    assert summary["records"] == 2
    assert summary["cpu"]["average_total"] == 20.0
    assert summary["memory"]["trend_used"] == 20
    assert "disk0" in summary["disk"]
