import json
from metrics_collector.reporter import summarize, generate_summary_from_file


def test_summarize_empty():
    assert summarize([]) == {}


def test_generate_and_summarize(tmp_path):
    path = tmp_path / 'm.jsonl'
    records = [
        {'timestamp': 1, 'cpu': {'total': 10, 'per_core': [10, 12]}, 'memory': {'total': 100, 'used': 40}, 'disk': {'/': {'total': 1000, 'used': 400}}, 'network': {'eth0': {'bytes_sent': 100, 'bytes_recv': 200}}},
        {'timestamp': 2, 'cpu': {'total': 30, 'per_core': [30, 32]}, 'memory': {'total': 100, 'used': 60}, 'disk': {'/': {'total': 1000, 'used': 600}}, 'network': {'eth0': {'bytes_sent': 200, 'bytes_recv': 300}}}
    ]
    with open(path, 'w', encoding='utf-8') as fh:
        for r in records:
            fh.write(json.dumps(r) + '\n')

    summary = generate_summary_from_file(str(path))
    assert summary['samples'] == 2
    assert 'cpu' in summary
    assert 'memory' in summary
    assert '/' in summary['disk']
    assert 'eth0' in summary['network']
