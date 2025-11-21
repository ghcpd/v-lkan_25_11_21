"""collector.py
Collects system metrics periodically using psutil.
"""
import time
import logging
from typing import Dict, Any, Optional

import psutil

logger = logging.getLogger(__name__)


def collect_once() -> Dict[str, Any]:
    """Collect a single snapshot of system metrics."""
    timestamp = int(time.time())

    cpu_total = psutil.cpu_percent(interval=None)
    per_core = psutil.cpu_percent(interval=None, percpu=True)

    vm = psutil.virtual_memory()
    memory = {
        "total": vm.total // 1024,  # in KB
        "used": vm.used // 1024,
        "free": getattr(vm, "free", 0) // 1024,
        "available": getattr(vm, "available", vm.free) // 1024,
    }

    disks = {}
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disks[part.device] = {
                "mountpoint": part.mountpoint,
                "total": usage.total // 1024,
                "used": usage.used // 1024,
                "free": usage.free // 1024,
            }
        except PermissionError:
            # Skip partitions that are not accessible
            logger.debug("Skipping partition %s, permission denied", part.device)

    net_io = psutil.net_io_counters(pernic=True)
    network = {}
    for nic, data in net_io.items():
        network[nic] = {"bytes_sent": data.bytes_sent, "bytes_recv": data.bytes_recv}

    payload = {
        "timestamp": timestamp,
        "cpu": {"total": cpu_total, "per_core": per_core},
        "memory": memory,
        "disk": disks,
        "network": network,
    }
    return payload


class Collector:
    def __init__(self, interval: int = 5, writer: Optional[callable] = None):
        self.interval = max(1, int(interval))
        self.writer = writer
        self._running = False

    def start(self):
        self._running = True
        logger.info("Starting collector with interval %s seconds", self.interval)
        try:
            while self._running:
                record = collect_once()
                if self.writer:
                    try:
                        self.writer(record)
                    except Exception as e:
                        logger.exception("Writer failed: %s", e)
                time.sleep(self.interval)
        except KeyboardInterrupt:
            logger.info("Collector stopped by KeyboardInterrupt")

    def stop(self):
        self._running = False
