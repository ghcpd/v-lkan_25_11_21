import json

from storage import JSONLStorage


def test_write_record_creates_file(tmp_path):
    storage = JSONLStorage(tmp_path / "metrics.jsonl")
    storage.write_record({"value": 1})

    data = (tmp_path / "metrics.jsonl").read_text(encoding="utf-8").strip()
    assert json.loads(data)["value"] == 1


def test_rotation_occurs(tmp_path):
    storage = JSONLStorage(tmp_path / "metrics.jsonl", max_bytes=50)
    for idx in range(10):
        storage.write_record({"value": "x" * idx})

    rotated = list(tmp_path.glob("metrics.jsonl.*"))
    assert rotated, "Expected at least one rotated file"
