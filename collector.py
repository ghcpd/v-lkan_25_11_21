#!/usr/bin/env python3
"""
Metrics Collector Module
Collects CPU, Memory, Disk, and Network metrics using psutil
"""

import psutil
import time
import logging
from typing import Dict, Any, List


class MetricsCollector:
    """Collects system metrics without requiring admin/root permissions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Initialize network counters for delta calculation
        self._last_net_io = psutil.net_io_counters(pernic=True)
        self._last_net_time = time.time()
    
    def collect_cpu_metrics(self) -> Dict[str, Any]:
        """
        Collect CPU metrics
        Returns:
            dict: CPU total usage and per-core usage
        """
        try:
            total_usage = psutil.cpu_percent(interval=0.1)
            per_core = psutil.cpu_percent(interval=0.1, percpu=True)
            
            return {
                "total": round(total_usage, 2),
                "per_core": [round(core, 2) for core in per_core]
            }
        except Exception as e:
            self.logger.error(f"Error collecting CPU metrics: {e}")
            return {"total": 0.0, "per_core": []}
    
    def collect_memory_metrics(self) -> Dict[str, int]:
        """
        Collect memory metrics
        Returns:
            dict: Total, used, free, and available memory in MB
        """
        try:
            mem = psutil.virtual_memory()
            return {
                "total": mem.total // (1024 * 1024),  # Convert to MB
                "used": mem.used // (1024 * 1024),
                "free": mem.free // (1024 * 1024),
                "available": mem.available // (1024 * 1024)
            }
        except Exception as e:
            self.logger.error(f"Error collecting memory metrics: {e}")
            return {"total": 0, "used": 0, "free": 0, "available": 0}
    
    def collect_disk_metrics(self) -> Dict[str, Dict[str, int]]:
        """
        Collect disk metrics for all partitions
        Returns:
            dict: Per-partition total, used, and free space in MB
        """
        disk_data = {}
        try:
            partitions = psutil.disk_partitions()
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_data[partition.mountpoint] = {
                        "total": usage.total // (1024 * 1024),  # Convert to MB
                        "used": usage.used // (1024 * 1024),
                        "free": usage.free // (1024 * 1024)
                    }
                except (PermissionError, OSError) as e:
                    # Skip partitions we can't access
                    self.logger.warning(f"Cannot access partition {partition.mountpoint}: {e}")
                    continue
        except Exception as e:
            self.logger.error(f"Error collecting disk metrics: {e}")
        
        return disk_data
    
    def collect_network_metrics(self) -> Dict[str, Dict[str, int]]:
        """
        Collect network metrics for all interfaces
        Returns:
            dict: Per-interface bytes sent and received
        """
        network_data = {}
        try:
            net_io = psutil.net_io_counters(pernic=True)
            
            for interface, counters in net_io.items():
                network_data[interface] = {
                    "bytes_sent": counters.bytes_sent,
                    "bytes_recv": counters.bytes_recv
                }
        except Exception as e:
            self.logger.error(f"Error collecting network metrics: {e}")
        
        return network_data
    
    def collect_all_metrics(self) -> Dict[str, Any]:
        """
        Collect all system metrics
        Returns:
            dict: Complete metrics snapshot with timestamp
        """
        timestamp = int(time.time())
        
        metrics = {
            "timestamp": timestamp,
            "cpu": self.collect_cpu_metrics(),
            "memory": self.collect_memory_metrics(),
            "disk": self.collect_disk_metrics(),
            "network": self.collect_network_metrics()
        }
        
        return metrics


if __name__ == "__main__":
    # Simple test
    logging.basicConfig(level=logging.INFO)
    collector = MetricsCollector()
    metrics = collector.collect_all_metrics()
    print(metrics)
