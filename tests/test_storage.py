import json
import os

from storage import MetricsWriter


def test_write_jsonl(tmp_path):
    writer = MetricsWriter(output_dir=str(tmp_path), filename_prefix="test")
    record = {"hello": "world"}
    path = writer.write(record)

    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    assert len(lines) == 1
    assert json.loads(lines[0]) == record


def test_size_rotation(tmp_path):
    writer = MetricsWriter(
        output_dir=str(tmp_path), filename_prefix="test", rotation={"type": "size", "max_bytes": 30, "backup_count": 2}
    )
    # Each record is small but will trigger rotation over multiple writes
    for i in range(10):
        writer.write({"i": i})

    files = [p.name for p in tmp_path.iterdir()]
    assert "test.jsonl" in files
    # At least one rotated file should exist
    assert any(name.startswith("test.jsonl.") for name in files)
