from reporter import summarize

def test_summarize_empty():
    assert summarize([]) == {}

def test_summarize_basic():
    records = [
        {'cpu': {'total': 10}, 'memory': {'used': 100}},
        {'cpu': {'total': 30}, 'memory': {'used': 300}},
    ]
    out = summarize(records)
    assert out['count'] == 2
    assert out['avg_cpu'] == 20
    assert out['avg_memory_used'] == 200
