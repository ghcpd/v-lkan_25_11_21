"""
Main metric collection module.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import time
from typing import Any, Dict

import psutil

from storage import MetricsWriter

LOGGER = logging.getLogger("collector")


def load_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def collect_metrics() -> Dict[str, Any]:
    """
    Collect CPU, memory, disk, and network metrics.
    Returns a dict ready to be serialized to JSON.
    """
    timestamp = int(time.time())

    # CPU
    # Single sampling to avoid double-refresh; small non-blocking interval=0.1 for a stable reading
    cpu_per_core = psutil.cpu_percent(interval=0.1, percpu=True)
    cpu_total = sum(cpu_per_core) / len(cpu_per_core) if cpu_per_core else 0.0

    # Memory
    vm = psutil.virtual_memory()
    memory = {
        "total": vm.total,
        "used": vm.used,
        "free": vm.free,
        "available": vm.available,
        "percent": vm.percent,
    }

    # Disk per partition
    disk = {}
    for part in psutil.disk_partitions(all=False):
        mountpoint = part.mountpoint
        try:
            usage = psutil.disk_usage(mountpoint)
        except PermissionError:
            continue
        # Use drive letter or mountpoint name as key
        key = part.device or mountpoint
        disk[key] = {
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percent": usage.percent,
        }

    # Network per interface
    net = {}
    net_io = psutil.net_io_counters(pernic=True)
    for iface, counters in net_io.items():
        net[iface] = {
            "bytes_sent": counters.bytes_sent,
            "bytes_recv": counters.bytes_recv,
            "packets_sent": counters.packets_sent,
            "packets_recv": counters.packets_recv,
            "errin": counters.errin,
            "errout": counters.errout,
            "dropin": counters.dropin,
            "dropout": counters.dropout,
        }

    return {
        "timestamp": timestamp,
        "cpu": {
            "total": cpu_total,
            "per_core": cpu_per_core,
        },
        "memory": memory,
        "disk": disk,
        "network": net,
    }


def run_collector(config_path: str) -> None:
    config = load_config(config_path)
    interval = float(config.get("collection_interval_seconds", 5))
    output_dir = config.get("output_dir", "data")
    prefix = config.get("metrics_filename_prefix", "metrics")
    rotation = config.get("rotation")

    writer = MetricsWriter(output_dir=output_dir, filename_prefix=prefix, rotation=rotation)

    LOGGER.info("Starting metrics collection: interval=%ss", interval)
    try:
        while True:
            record = collect_metrics()
            writer.write(record)
            time.sleep(interval)
    except KeyboardInterrupt:
        LOGGER.info("Metrics collection stopped by user")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
    parser = argparse.ArgumentParser(description="System metrics collector")
    parser.add_argument("--config", type=str, default="config.json", help="Path to config.json")
    args = parser.parse_args()

    cfg_path = args.config
    if not os.path.exists(cfg_path):
        raise FileNotFoundError(f"Config file not found: {cfg_path}")

    run_collector(cfg_path)
