from storage import JsonlWriter
import time
import os

def write_demo_records(path: str, count: int = 3):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with JsonlWriter(path) as w:
        for i in range(count):
            rec = {
                'timestamp': int(time.time()),
                'cpu': {'total': float(i*10+5), 'per_core': [float(i*5+1), float(i*5+2)]},
                'memory': {'total': 16384, 'used': 8192 + i, 'free': 4096, 'available': 8192 + i},
                'disk': {'C:': {'total': 512000, 'used': 256000 + i, 'free': 256000 - i}},
                'network': {'eth0': {'bytes_sent': 1000 + i, 'bytes_recv': 2000 + i}}
            }
            w.write(rec)
            time.sleep(0.05)

if __name__ == '__main__':
    write_demo_records('data/metrics.jsonl', 3)
    print('wrote records to data/metrics.jsonl')
