import time
import json
import threading
from typing import Dict, Any
import psutil
from pathlib import Path

from storage import JSONLStorage

class SystemCollector:
    def __init__(self, storage: JSONLStorage, interval: int = 5):
        self.storage = storage
        self.interval = interval
        self.running = False
        self._thread = None

    def collect_once(self) -> Dict[str, Any]:
        timestamp = int(time.time())
        cpu_total = psutil.cpu_percent(interval=None)
        cpu_per_core = psutil.cpu_percent(percpu=True)
        mem = psutil.virtual_memory()
        disk_parts = {}
        for part in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(part.mountpoint)
                disk_parts[part.device or part.mountpoint] = {
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                }
            except PermissionError:
                continue
        net_io = psutil.net_io_counters(pernic=True)
        networks = {iface: {"bytes_sent": v.bytes_sent, "bytes_recv": v.bytes_recv} for iface, v in net_io.items()}

        record = {
            "timestamp": timestamp,
            "cpu": {"total": cpu_total, "per_core": cpu_per_core},
            "memory": {"total": mem.total, "used": mem.used, "free": mem.free, "available": getattr(mem, 'available', None)},
            "disk": disk_parts,
            "network": networks,
        }
        return record

    def start(self):
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join(timeout=1)

    def _loop(self):
        while self.running:
            record = self.collect_once()
            self.storage.write(record)
            time.sleep(self.interval)

if __name__ == "__main__":
    import json
    cfg = json.loads(Path('config.json').read_text())
    Path(cfg['output_dir']).mkdir(parents=True, exist_ok=True)
    storage = JSONLStorage(cfg['jsonl_file'], rotate_after_mb=cfg.get('rotate_after_mb', 5))
    collector = SystemCollector(storage, cfg.get('collection_interval_seconds', 5))
    try:
        collector.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        collector.stop()
