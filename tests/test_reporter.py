import os
import json
from reporter import aggregate, generate_summary_from_file
from storage import JsonlWriter

def create_sample_jsonl(tmp_path):
    f = tmp_path / "metrics.jsonl"
    writer = JsonlWriter(str(f))
    for i in range(5):
        writer.write({"timestamp": 100 + i, "cpu": {"total": 10 * i, "per_core": [10 * i, 5 * i]}, "memory": {"used": 1000 + i}})
    writer.close()
    return str(f)

def test_aggregate_single():
    recs = [
        {"timestamp": 1, "cpu": {"total": 10, "per_core": [5, 5]}, "memory": {"used": 100}},
        {"timestamp": 2, "cpu": {"total": 20, "per_core": [10, 10]}, "memory": {"used": 200}},
    ]
    summary = aggregate(recs)
    assert summary['cpu']['total_avg'] == 15
    assert summary['cpu']['per_core_avg'][0] == 7.5

def test_generate_summary(tmp_path):
    path = create_sample_jsonl(tmp_path)
    summary = generate_summary_from_file(path)
    assert summary['count'] == 5
    assert 'cpu' in summary
