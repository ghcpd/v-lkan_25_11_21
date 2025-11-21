#!/usr/bin/env python3
"""
Storage Module
Handles writing metrics to JSONL files with rotation support
"""

import json
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


class MetricsStorage:
    """Manages storage of metrics data in JSONL format"""
    
    def __init__(self, output_dir: str, metrics_file: str, 
                 max_file_size_mb: int = 100, rotate_files: bool = True):
        """
        Initialize storage handler
        
        Args:
            output_dir: Directory to store metrics files
            metrics_file: Name of the metrics file
            max_file_size_mb: Maximum file size before rotation
            rotate_files: Whether to rotate files when size limit reached
        """
        self.output_dir = Path(output_dir)
        self.metrics_file = metrics_file
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        self.rotate_files = rotate_files
        self.logger = logging.getLogger(__name__)
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_file_path = self.output_dir / self.metrics_file
    
    def _should_rotate(self) -> bool:
        """Check if current file should be rotated"""
        if not self.rotate_files:
            return False
        
        if not self.current_file_path.exists():
            return False
        
        file_size = self.current_file_path.stat().st_size
        return file_size >= self.max_file_size_bytes
    
    def _rotate_file(self) -> None:
        """Rotate the current metrics file"""
        if not self.current_file_path.exists():
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = self.current_file_path.stem
        extension = self.current_file_path.suffix
        
        rotated_name = f"{base_name}_{timestamp}{extension}"
        rotated_path = self.output_dir / rotated_name
        
        try:
            self.current_file_path.rename(rotated_path)
            self.logger.info(f"Rotated metrics file to {rotated_name}")
        except Exception as e:
            self.logger.error(f"Error rotating file: {e}")
    
    def write_metric(self, metric_data: Dict[str, Any]) -> bool:
        """
        Write a single metric record to JSONL file
        
        Args:
            metric_data: Dictionary containing metric data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if rotation is needed
            if self._should_rotate():
                self._rotate_file()
            
            # Append metric as JSON line
            with open(self.current_file_path, 'a', encoding='utf-8') as f:
                json.dump(metric_data, f, separators=(',', ':'))
                f.write('\n')
            
            return True
        except Exception as e:
            self.logger.error(f"Error writing metric: {e}")
            return False
    
    def write_metrics_batch(self, metrics: list) -> int:
        """
        Write multiple metrics at once
        
        Args:
            metrics: List of metric dictionaries
            
        Returns:
            int: Number of metrics successfully written
        """
        written_count = 0
        for metric in metrics:
            if self.write_metric(metric):
                written_count += 1
        
        return written_count
    
    def read_metrics(self, limit: int = None) -> list:
        """
        Read metrics from current file
        
        Args:
            limit: Maximum number of records to read (None for all)
            
        Returns:
            list: List of metric dictionaries
        """
        metrics = []
        
        if not self.current_file_path.exists():
            return metrics
        
        try:
            with open(self.current_file_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if limit and i >= limit:
                        break
                    
                    try:
                        metric = json.loads(line.strip())
                        metrics.append(metric)
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"Invalid JSON on line {i+1}: {e}")
                        continue
        except Exception as e:
            self.logger.error(f"Error reading metrics: {e}")
        
        return metrics
    
    def get_file_info(self) -> Dict[str, Any]:
        """
        Get information about current metrics file
        
        Returns:
            dict: File information including size and record count
        """
        info = {
            "path": str(self.current_file_path),
            "exists": self.current_file_path.exists(),
            "size_bytes": 0,
            "size_mb": 0.0,
            "record_count": 0
        }
        
        if self.current_file_path.exists():
            info["size_bytes"] = self.current_file_path.stat().st_size
            info["size_mb"] = round(info["size_bytes"] / (1024 * 1024), 2)
            
            # Count records
            try:
                with open(self.current_file_path, 'r', encoding='utf-8') as f:
                    info["record_count"] = sum(1 for _ in f)
            except Exception as e:
                self.logger.error(f"Error counting records: {e}")
        
        return info


if __name__ == "__main__":
    # Simple test
    logging.basicConfig(level=logging.INFO)
    storage = MetricsStorage("data", "test_metrics.jsonl")
    
    test_metric = {
        "timestamp": 1234567890,
        "cpu": {"total": 50.0, "per_core": [45.0, 55.0]},
        "memory": {"total": 8192, "used": 4096, "free": 4096, "available": 4096}
    }
    
    storage.write_metric(test_metric)
    print(storage.get_file_info())
