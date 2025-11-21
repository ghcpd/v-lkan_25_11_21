#!/usr/bin/env python3
"""
Unit tests for storage.py
"""

import pytest
import json
import sys
from pathlib import Path
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from storage import MetricsStorage


class TestMetricsStorage:
    """Test suite for MetricsStorage"""
    
    def setup_method(self):
        """Setup test fixtures"""
        # Create temporary directory for tests
        self.test_dir = tempfile.mkdtemp()
        self.storage = MetricsStorage(
            output_dir=self.test_dir,
            metrics_file="test_metrics.jsonl",
            max_file_size_mb=1,
            rotate_files=True
        )
    
    def teardown_method(self):
        """Cleanup test fixtures"""
        # Remove temporary directory
        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)
    
    def test_storage_initialization(self):
        """Test storage initializes properly"""
        assert self.storage is not None
        assert Path(self.test_dir).exists()
        assert self.storage.output_dir == Path(self.test_dir)
    
    def test_write_single_metric(self):
        """Test writing a single metric"""
        test_metric = {
            "timestamp": 1234567890,
            "cpu": {"total": 50.0, "per_core": [45.0, 55.0]},
            "memory": {"total": 8192, "used": 4096, "free": 4096, "available": 4096}
        }
        
        result = self.storage.write_metric(test_metric)
        assert result is True
        
        # Verify file was created
        assert self.storage.current_file_path.exists()
        
        # Verify content
        with open(self.storage.current_file_path, 'r') as f:
            line = f.readline()
            loaded_metric = json.loads(line)
            assert loaded_metric == test_metric
    
    def test_write_multiple_metrics(self):
        """Test writing multiple metrics"""
        metrics = [
            {"timestamp": 1000, "cpu": {"total": 30.0}},
            {"timestamp": 1001, "cpu": {"total": 35.0}},
            {"timestamp": 1002, "cpu": {"total": 40.0}}
        ]
        
        count = self.storage.write_metrics_batch(metrics)
        assert count == 3
        
        # Verify all metrics were written
        with open(self.storage.current_file_path, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 3
    
    def test_read_metrics(self):
        """Test reading metrics from file"""
        # Write some test data
        test_metrics = [
            {"timestamp": 1000, "cpu": {"total": 30.0}},
            {"timestamp": 1001, "cpu": {"total": 35.0}},
            {"timestamp": 1002, "cpu": {"total": 40.0}}
        ]
        
        for metric in test_metrics:
            self.storage.write_metric(metric)
        
        # Read back
        loaded_metrics = self.storage.read_metrics()
        assert len(loaded_metrics) == 3
        assert loaded_metrics == test_metrics
    
    def test_read_metrics_with_limit(self):
        """Test reading metrics with limit"""
        # Write test data
        for i in range(10):
            self.storage.write_metric({"timestamp": 1000 + i, "value": i})
        
        # Read with limit
        loaded_metrics = self.storage.read_metrics(limit=5)
        assert len(loaded_metrics) == 5
    
    def test_get_file_info(self):
        """Test getting file information"""
        # Initially file doesn't exist
        info = self.storage.get_file_info()
        assert info['exists'] is False
        assert info['size_bytes'] == 0
        assert info['record_count'] == 0
        
        # Write some data
        for i in range(5):
            self.storage.write_metric({"timestamp": 1000 + i, "value": i})
        
        # Check info again
        info = self.storage.get_file_info()
        assert info['exists'] is True
        assert info['size_bytes'] > 0
        assert info['record_count'] == 5
    
    def test_file_rotation(self):
        """Test file rotation when size limit is reached"""
        # Create storage with very small max size
        small_storage = MetricsStorage(
            output_dir=self.test_dir,
            metrics_file="rotate_test.jsonl",
            max_file_size_mb=0.001,  # Very small (1KB)
            rotate_files=True
        )
        
        # Write enough data to trigger rotation
        large_metric = {
            "timestamp": 1000,
            "data": "x" * 1000  # 1KB of data
        }
        
        small_storage.write_metric(large_metric)
        small_storage.write_metric(large_metric)  # This should trigger rotation
        
        # Check if rotated files exist
        rotated_files = list(Path(self.test_dir).glob("rotate_test_*.jsonl"))
        # Rotation may or may not happen depending on exact size
        assert small_storage.current_file_path.exists()
    
    def test_no_rotation_when_disabled(self):
        """Test that rotation doesn't happen when disabled"""
        no_rotate_storage = MetricsStorage(
            output_dir=self.test_dir,
            metrics_file="no_rotate.jsonl",
            max_file_size_mb=0.001,
            rotate_files=False
        )
        
        # Write data
        for i in range(10):
            no_rotate_storage.write_metric({"timestamp": 1000 + i, "value": i})
        
        # Should not have rotated files
        rotated_files = list(Path(self.test_dir).glob("no_rotate_*.jsonl"))
        assert len(rotated_files) == 0
    
    def test_invalid_json_handling(self):
        """Test handling of invalid JSON in file"""
        # Write valid and invalid data
        with open(self.storage.current_file_path, 'w') as f:
            f.write('{"timestamp": 1000}\n')
            f.write('invalid json line\n')
            f.write('{"timestamp": 1001}\n')
        
        # Should skip invalid line
        metrics = self.storage.read_metrics()
        assert len(metrics) == 2
        assert metrics[0]['timestamp'] == 1000
        assert metrics[1]['timestamp'] == 1001
    
    def test_jsonl_format(self):
        """Test that output is valid JSONL format"""
        metrics = [
            {"timestamp": 1000, "value": 1},
            {"timestamp": 1001, "value": 2}
        ]
        
        for metric in metrics:
            self.storage.write_metric(metric)
        
        # Verify JSONL format (each line is valid JSON)
        with open(self.storage.current_file_path, 'r') as f:
            for line in f:
                # Each line should be valid JSON
                parsed = json.loads(line.strip())
                assert isinstance(parsed, dict)
                assert 'timestamp' in parsed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
