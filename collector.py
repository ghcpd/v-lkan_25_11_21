"""
Metric collection entrypoint that gathers CPU, memory, disk, and network stats.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional

import psutil

from storage import JSONLStorage


def load_config(path: str | Path) -> Dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


class MetricCollector:
    """Polls local system statistics and persists them via the provided storage backend."""

    def __init__(self, storage: JSONLStorage, interval: float = 5.0) -> None:
        self.storage = storage
        self.interval = max(interval, 0.5)
        # Prime CPU percent measurements so the first sample is meaningful.
        psutil.cpu_percent(interval=None, percpu=True)

    def _collect_cpu(self) -> Dict[str, Any]:
        per_core = psutil.cpu_percent(interval=None, percpu=True)
        if not per_core:
            total = 0.0
        else:
            total = sum(per_core) / len(per_core)
        return {"total": total, "per_core": per_core}

    def _collect_memory(self) -> Dict[str, Any]:
        vm = psutil.virtual_memory()
        return {
            "total": vm.total,
            "used": vm.used,
            "free": vm.free,
            "available": vm.available,
        }

    def _collect_disk(self) -> Dict[str, Any]:
        disk_info: Dict[str, Dict[str, int]] = {}
        for partition in psutil.disk_partitions(all=False):
            device_name = partition.device.rstrip("\\") if partition.device else partition.mountpoint
            try:
                usage = psutil.disk_usage(partition.mountpoint)
            except PermissionError:
                continue
            disk_info[device_name] = {
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
            }
        return disk_info

    def _collect_network(self) -> Dict[str, Any]:
        stats: Dict[str, Dict[str, int]] = {}
        for name, counters in psutil.net_io_counters(pernic=True).items():
            stats[name] = {
                "bytes_sent": counters.bytes_sent,
                "bytes_recv": counters.bytes_recv,
            }
        return stats

    def collect_once(self) -> Dict[str, Any]:
        timestamp = time.time()
        record = {
            "timestamp": int(timestamp),
            "cpu": self._collect_cpu(),
            "memory": self._collect_memory(),
            "disk": self._collect_disk(),
            "network": self._collect_network(),
        }
        return record

    def run(self, duration: Optional[float] = None) -> None:
        end_time = None if duration is None else (time.time() + duration)
        while True:
            start = time.time()
            record = self.collect_once()
            self.storage.write_record(record)
            if end_time is not None and time.time() >= end_time:
                break
            elapsed = time.time() - start
            sleep_for = max(self.interval - elapsed, 0.0)
            time.sleep(sleep_for)
            if end_time is not None and time.time() >= end_time:
                break


def build_storage(config: Dict[str, Any]) -> JSONLStorage:
    output_path = config.get("output_path", "output/metrics.jsonl")
    max_bytes = config.get("max_file_size_bytes", 5 * 1024 * 1024)
    return JSONLStorage(output_path, max_bytes=max_bytes)


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect local system metrics to JSONL.")
    parser.add_argument("--config", default="config.json", help="Path to config.json")
    parser.add_argument("--duration", type=float, default=None, help="Optional run duration in seconds")
    parser.add_argument("--output", default=None, help="Override output file path")
    args = parser.parse_args()

    config = load_config(args.config)
    if args.output:
        config["output_path"] = args.output
    interval = float(config.get("collection_interval", 5))
    storage = build_storage(config)

    collector = MetricCollector(storage, interval=interval)
    collector.run(duration=args.duration)


if __name__ == "__main__":
    main()
