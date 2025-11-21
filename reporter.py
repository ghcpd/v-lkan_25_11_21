#!/usr/bin/env python3
"""
Reporter Module
Generates summary reports from collected metrics
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from statistics import mean, median
from collections import defaultdict


class MetricsReporter:
    """Generates summary reports from metrics data"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def load_metrics_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load metrics from a JSONL file
        
        Args:
            file_path: Path to JSONL metrics file
            
        Returns:
            list: List of metric dictionaries
        """
        metrics = []
        path = Path(file_path)
        
        if not path.exists():
            self.logger.error(f"File not found: {file_path}")
            return metrics
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        metric = json.loads(line.strip())
                        metrics.append(metric)
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"Invalid JSON at line {line_num}: {e}")
        except Exception as e:
            self.logger.error(f"Error reading file: {e}")
        
        return metrics
    
    def analyze_cpu_metrics(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze CPU metrics"""
        cpu_totals = []
        cpu_cores_data = defaultdict(list)
        
        for metric in metrics:
            if 'cpu' in metric and 'total' in metric['cpu']:
                cpu_totals.append(metric['cpu']['total'])
                
                if 'per_core' in metric['cpu']:
                    for core_idx, usage in enumerate(metric['cpu']['per_core']):
                        cpu_cores_data[core_idx].append(usage)
        
        analysis = {
            "total": {
                "average": round(mean(cpu_totals), 2) if cpu_totals else 0.0,
                "median": round(median(cpu_totals), 2) if cpu_totals else 0.0,
                "min": round(min(cpu_totals), 2) if cpu_totals else 0.0,
                "max": round(max(cpu_totals), 2) if cpu_totals else 0.0,
                "samples": len(cpu_totals)
            },
            "per_core": {}
        }
        
        for core_idx, values in cpu_cores_data.items():
            analysis["per_core"][f"core_{core_idx}"] = {
                "average": round(mean(values), 2) if values else 0.0,
                "min": round(min(values), 2) if values else 0.0,
                "max": round(max(values), 2) if values else 0.0
            }
        
        return analysis
    
    def analyze_memory_metrics(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze memory metrics"""
        memory_data = {
            'used': [],
            'free': [],
            'available': []
        }
        total_memory = 0
        
        for metric in metrics:
            if 'memory' in metric:
                mem = metric['memory']
                if 'total' in mem:
                    total_memory = mem['total']
                if 'used' in mem:
                    memory_data['used'].append(mem['used'])
                if 'free' in mem:
                    memory_data['free'].append(mem['free'])
                if 'available' in mem:
                    memory_data['available'].append(mem['available'])
        
        analysis = {
            "total_mb": total_memory,
            "used": {
                "average_mb": round(mean(memory_data['used']), 2) if memory_data['used'] else 0.0,
                "min_mb": min(memory_data['used']) if memory_data['used'] else 0,
                "max_mb": max(memory_data['used']) if memory_data['used'] else 0
            },
            "available": {
                "average_mb": round(mean(memory_data['available']), 2) if memory_data['available'] else 0.0,
                "min_mb": min(memory_data['available']) if memory_data['available'] else 0,
                "max_mb": max(memory_data['available']) if memory_data['available'] else 0
            },
            "samples": len(memory_data['used'])
        }
        
        return analysis
    
    def analyze_disk_metrics(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze disk metrics"""
        disk_data = defaultdict(lambda: {'used': [], 'free': [], 'total': 0})
        
        for metric in metrics:
            if 'disk' in metric:
                for partition, stats in metric['disk'].items():
                    if 'total' in stats:
                        disk_data[partition]['total'] = stats['total']
                    if 'used' in stats:
                        disk_data[partition]['used'].append(stats['used'])
                    if 'free' in stats:
                        disk_data[partition]['free'].append(stats['free'])
        
        analysis = {}
        for partition, data in disk_data.items():
            analysis[partition] = {
                "total_mb": data['total'],
                "used": {
                    "average_mb": round(mean(data['used']), 2) if data['used'] else 0.0,
                    "min_mb": min(data['used']) if data['used'] else 0,
                    "max_mb": max(data['used']) if data['used'] else 0
                },
                "free": {
                    "average_mb": round(mean(data['free']), 2) if data['free'] else 0.0,
                    "min_mb": min(data['free']) if data['free'] else 0,
                    "max_mb": max(data['free']) if data['free'] else 0
                }
            }
        
        return analysis
    
    def analyze_network_metrics(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze network metrics"""
        network_data = defaultdict(lambda: {'bytes_sent': [], 'bytes_recv': []})
        
        for metric in metrics:
            if 'network' in metric:
                for interface, stats in metric['network'].items():
                    if 'bytes_sent' in stats:
                        network_data[interface]['bytes_sent'].append(stats['bytes_sent'])
                    if 'bytes_recv' in stats:
                        network_data[interface]['bytes_recv'].append(stats['bytes_recv'])
        
        analysis = {}
        for interface, data in network_data.items():
            # Calculate deltas (difference between first and last sample)
            sent_delta = 0
            recv_delta = 0
            
            if len(data['bytes_sent']) >= 2:
                sent_delta = data['bytes_sent'][-1] - data['bytes_sent'][0]
            if len(data['bytes_recv']) >= 2:
                recv_delta = data['bytes_recv'][-1] - data['bytes_recv'][0]
            
            analysis[interface] = {
                "total_bytes_sent": data['bytes_sent'][-1] if data['bytes_sent'] else 0,
                "total_bytes_recv": data['bytes_recv'][-1] if data['bytes_recv'] else 0,
                "delta_bytes_sent": sent_delta,
                "delta_bytes_recv": recv_delta,
                "samples": len(data['bytes_sent'])
            }
        
        return analysis
    
    def generate_summary_report(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate comprehensive summary report
        
        Args:
            metrics: List of metric dictionaries
            
        Returns:
            dict: Summary report
        """
        if not metrics:
            return {"error": "No metrics provided"}
        
        # Extract time window
        timestamps = [m['timestamp'] for m in metrics if 'timestamp' in m]
        time_window = {
            "start": min(timestamps) if timestamps else 0,
            "end": max(timestamps) if timestamps else 0,
            "duration_seconds": (max(timestamps) - min(timestamps)) if timestamps else 0,
            "sample_count": len(metrics)
        }
        
        report = {
            "generated_at": int(__import__('time').time()),
            "time_window": time_window,
            "cpu_analysis": self.analyze_cpu_metrics(metrics),
            "memory_analysis": self.analyze_memory_metrics(metrics),
            "disk_analysis": self.analyze_disk_metrics(metrics),
            "network_analysis": self.analyze_network_metrics(metrics)
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], output_path: str) -> bool:
        """
        Save report to JSON file
        
        Args:
            report: Report dictionary
            output_path: Output file path
            
        Returns:
            bool: True if successful
        """
        try:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"Report saved to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving report: {e}")
            return False
    
    def generate_and_save_report(self, input_file: str, output_file: str) -> bool:
        """
        Load metrics, generate report, and save
        
        Args:
            input_file: Input JSONL metrics file
            output_file: Output JSON report file
            
        Returns:
            bool: True if successful
        """
        metrics = self.load_metrics_from_file(input_file)
        if not metrics:
            self.logger.error("No metrics loaded")
            return False
        
        report = self.generate_summary_report(metrics)
        return self.save_report(report, output_file)


if __name__ == "__main__":
    # Simple test
    logging.basicConfig(level=logging.INFO)
    reporter = MetricsReporter()
    
    # Test with sample data
    sample_metrics = [
        {
            "timestamp": 1000,
            "cpu": {"total": 30.0, "per_core": [25.0, 35.0]},
            "memory": {"total": 8192, "used": 4000, "free": 4192, "available": 4192}
        },
        {
            "timestamp": 1005,
            "cpu": {"total": 40.0, "per_core": [35.0, 45.0]},
            "memory": {"total": 8192, "used": 4500, "free": 3692, "available": 3692}
        }
    ]
    
    report = reporter.generate_summary_report(sample_metrics)
    print(json.dumps(report, indent=2))
