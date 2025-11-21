import time
import os
from metrics_collector.collector import collect_once, Collector


def test_collect_once_structure():
    data = collect_once()
    assert 'timestamp' in data
    assert isinstance(data['cpu'], dict)
    assert 'total' in data['cpu']
    assert 'per_core' in data['cpu']
    assert isinstance(data['memory'], dict)


def test_collector_writer(tmp_path):
    out = tmp_path / 'out.jsonl'
    written = []

    def writer(record):
        written.append(record)
        with open(out, 'a', encoding='utf-8') as fh:
            fh.write(str(record) + "\n")

    c = Collector(interval=1, writer=writer)
    # run only 2 loops
    import threading

    t = threading.Thread(target=c.start, daemon=True)
    t.start()
    time.sleep(2.5)
    c.stop()
    t.join(timeout=2)
    assert len(written) >= 2
    assert os.path.exists(out)
