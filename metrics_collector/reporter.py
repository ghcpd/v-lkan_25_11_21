"""reporter.py
Generate summary reports from JSONL metric files.
"""
import json
import os
from typing import Dict, Any, Optional, Iterable


def read_jsonl(path: str) -> Iterable[Dict[str, Any]]:
    with open(path, 'r', encoding='utf-8') as fh:
        for line in fh:
            if not line.strip():
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def summarize(records: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    """Return aggregated summary for a list/iterator of records."""
    count = 0
    cpu_total_acc = 0.0
    per_core_acc = []

    mem_used_acc = 0
    mem_total_acc = 0

    disk_stats = {}
    net_stats = {}

    for r in records:
        count += 1
        cpu = r.get('cpu', {})
        cpu_total_acc += float(cpu.get('total', 0))
        per_core = cpu.get('per_core', [])
        # expand per_core_acc
        if len(per_core_acc) < len(per_core):
            per_core_acc.extend([0.0] * (len(per_core) - len(per_core_acc)))
        for i, v in enumerate(per_core):
            per_core_acc[i] += float(v)

        mem = r.get('memory', {})
        mem_used_acc += int(mem.get('used', 0))
        mem_total_acc += int(mem.get('total', 0))

        disk = r.get('disk', {})
        for name, d in disk.items():
            dd = disk_stats.setdefault(name, {'total': 0, 'used': 0, 'samples': 0})
            dd['total'] += int(d.get('total', 0))
            dd['used'] += int(d.get('used', 0))
            dd['samples'] += 1

        net = r.get('network', {})
        for nic, n in net.items():
            nd = net_stats.setdefault(nic, {'bytes_sent': 0, 'bytes_recv': 0, 'samples': 0})
            nd['bytes_sent'] += int(n.get('bytes_sent', 0))
            nd['bytes_recv'] += int(n.get('bytes_recv', 0))
            nd['samples'] += 1

    if count == 0:
        return {}

    summary = {
        'samples': count,
        'cpu': {
            'avg_total': cpu_total_acc / count,
            'avg_per_core': [x / count for x in per_core_acc],
        },
        'memory': {
            'avg_used': mem_used_acc // count,
            'avg_total': mem_total_acc // count,
        },
        'disk': {},
        'network': {},
    }

    for k, v in disk_stats.items():
        if v['samples']:
            summary['disk'][k] = {
                'avg_total': v['total'] // v['samples'],
                'avg_used': v['used'] // v['samples'],
            }

    for k, v in net_stats.items():
        if v['samples']:
            summary['network'][k] = {
                'avg_bytes_sent': v['bytes_sent'] // v['samples'],
                'avg_bytes_recv': v['bytes_recv'] // v['samples'],
            }

    return summary


def generate_summary_from_file(path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    records = list(read_jsonl(path))
    summary = summarize(records)
    if output_path:
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as fh:
            json.dump(summary, fh, indent=2)
    return summary


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: python reporter.py <input.jsonl> [output.json]')
        raise SystemExit(1)
    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    s = generate_summary_from_file(inp, out)
    print(json.dumps(s, indent=2))
