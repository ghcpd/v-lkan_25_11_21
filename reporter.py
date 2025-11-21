import json
from typing import List, Dict, Any
from statistics import mean

def summarize(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not records:
        return {}
    cpu_totals = [r['cpu']['total'] for r in records if 'cpu' in r and 'total' in r['cpu']]
    mem_used = [r['memory']['used'] for r in records if 'memory' in r and 'used' in r['memory']]

    avg_cpu = mean(cpu_totals) if cpu_totals else None
    avg_mem_used = mean(mem_used) if mem_used else None

    return {
        'count': len(records),
        'avg_cpu': avg_cpu,
        'avg_memory_used': avg_mem_used,
    }

def summarize_jsonl(path: str) -> Dict[str, Any]:
    records = []
    with open(path, 'r', encoding='utf-8') as fh:
        for line in fh:
            try:
                records.append(json.loads(line))
            except Exception:
                continue
    return summarize(records)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    args = parser.parse_args()
    print(json.dumps(summarize_jsonl(args.input), indent=2))
