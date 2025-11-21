import json
from reporter import generate_summary_from_file
import os

def save_disk_summary(jsonl_path: str, out_path: str = 'data/disk_summary.json'):
    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    summary = generate_summary_from_file(jsonl_path)
    disk_summary = summary.get('disk', {})
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(disk_summary, f, indent=2)
    return disk_summary

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--jsonl', default='data/metrics.jsonl', help='Path to JSONL metrics file')
    parser.add_argument('--out', default='data/disk_summary.json', help='Output JSON path')
    args = parser.parse_args()
    ds = save_disk_summary(args.jsonl, args.out)
    print(json.dumps(ds, indent=2))
