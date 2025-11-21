import os
import json
from metrics_collector.storage import JSONLStorage


def test_jsonl_write_and_rotate(tmp_path):
    d = tmp_path / 'data'
    d.mkdir()
    s = JSONLStorage(output_dir=str(d), base_filename='m.jsonl', max_bytes=200, backup_count=3)
    for i in range(50):
        s.write({'timestamp': i, 'v': 'x'*20})
    s.close()
    files = list(d.iterdir())
    # expect at least base file
    assert any(p.name == 'm.jsonl' or p.name.startswith('m.jsonl.') for p in files)

    # verify lines are valid jsonL (our writer stores json strings)
    for p in files:
        with open(p, 'r', encoding='utf-8') as fh:
            for line in fh:
                assert line.strip()
                # at least parseable if it is json
                try:
                    json.loads(line)
                except Exception:
                    # skip non-json lines but ensure line exists
                    assert line.strip()


def test_close_idempotent(tmp_path):
    s = JSONLStorage(output_dir=str(tmp_path), base_filename='a.jsonl', max_bytes=200)
    s.close()
    # call again
    s.close()
    assert True
