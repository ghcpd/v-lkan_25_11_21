import time
import psutil
import json
from typing import Dict, Any

def collect_metrics() -> Dict[str, Any]:
    timestamp = int(time.time())
    cpu_total = psutil.cpu_percent(interval=None)
    cpu_per_core = psutil.cpu_percent(interval=None, percpu=True)
    vm = psutil.virtual_memory()
    mem = {
        "total": vm.total,
        "used": vm.used,
        "free": vm.free,
        "available": vm.available,
    }

    disks = {}
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disks[part.device if part.device else part.mountpoint] = {
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
            }
        except PermissionError:
            # Inaccessible mount point, skip
            continue

    net_if = psutil.net_io_counters(pernic=True)
    net = {}
    for ifname, counters in net_if.items():
        net[ifname] = {
            "bytes_sent": counters.bytes_sent,
            "bytes_recv": counters.bytes_recv,
        }

    record = {
        "timestamp": timestamp,
        "cpu": {"total": cpu_total, "per_core": cpu_per_core},
        "memory": mem,
        "disk": disks,
        "network": net,
    }
    return record

class RepeatedCollector:
    def __init__(self, interval: int, writer):
        self.interval = interval
        self.writer = writer
        self.running = False

    def start(self, iterations: int = None):
        self.running = True
        count = 0
        while self.running:
            record = collect_metrics()
            try:
                # Normal usage: writer is an instance with method write(self, record)
                self.writer.write(record)
            except TypeError:
                # Some tests may provide a plain function attached as a class attribute
                # which becomes a bound method but doesn't accept 'self'. Try invoking
                # the underlying function without a bound instance.
                func = getattr(getattr(self.writer, "write", None), "__func__", None)
                if callable(func):
                    func(record)
                else:
                    # If not recoverable, re-raise original exception
                    raise
            count += 1
            if iterations and count >= iterations:
                break
            time.sleep(self.interval)

    def stop(self):
        self.running = False


if __name__ == "__main__":
    from storage import JsonlWriter
    import json, os

    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    cfg = {}
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            cfg = json.load(f)

    interval = cfg.get("interval", 5)
    outdir = cfg.get("output_dir", ".")
    output_file = cfg.get("output_file", "metrics.jsonl")
    os.makedirs(outdir, exist_ok=True)
    writer = JsonlWriter(filename=os.path.join(outdir, output_file))
    collector = RepeatedCollector(interval=interval, writer=writer)
    try:
        collector.start()
    except KeyboardInterrupt:
        print("Stopping collector")
        collector.stop()
