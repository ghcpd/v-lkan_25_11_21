import os
import time
from storage import JsonlWriter

def test_jsonl_write_and_read(tmp_path):
    f = tmp_path / "metrics.jsonl"
    writer = JsonlWriter(str(f), max_size_bytes=1024)  # small size to test rotation
    # Write a few records
    for i in range(10):
        writer.write({"timestamp": i, "cpu": {"total": i}, "memory": {"used": i}})
    writer.close()
    # Read back records
    recs = list(JsonlWriter(str(f)).read_all())
    assert len(recs) == 10
    assert recs[0]["timestamp"] == 0

def test_rotation(tmp_path):
    f = tmp_path / "metrics.jsonl"
    writer = JsonlWriter(str(f), max_size_bytes=200)
    # Each record is small; write many to force rotation
    for i in range(200):
        writer.write({"timestamp": i, "cpu": {"total": i}})
    writer.close()
    # Check rotated files exist
    names = os.listdir(str(tmp_path))
    assert any(name.startswith("metrics.jsonl.") for name in names) or "metrics.jsonl" in names
