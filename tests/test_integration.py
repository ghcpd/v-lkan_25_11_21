#!/usr/bin/env python3
"""
Integration tests for the complete metrics system
"""

import pytest
import sys
import time
import json
from pathlib import Path
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from collector import MetricsCollector
from storage import MetricsStorage
from reporter import MetricsReporter


class TestIntegration:
    """Integration tests for complete workflow"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.collector = MetricsCollector()
        self.storage = MetricsStorage(
            output_dir=self.test_dir,
            metrics_file="integration_metrics.jsonl"
        )
        self.reporter = MetricsReporter()
    
    def teardown_method(self):
        """Cleanup test fixtures"""
        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)
    
    def test_end_to_end_workflow(self):
        """Test complete workflow: collect -> store -> report"""
        # Step 1: Collect metrics
        metrics = []
        for _ in range(3):
            metric = self.collector.collect_all_metrics()
            metrics.append(metric)
            time.sleep(0.1)  # Small delay between collections
        
        # Step 2: Store metrics
        for metric in metrics:
            result = self.storage.write_metric(metric)
            assert result is True
        
        # Step 3: Verify storage
        file_info = self.storage.get_file_info()
        assert file_info['exists'] is True
        assert file_info['record_count'] == 3
        
        # Step 4: Generate report
        metrics_file = self.storage.current_file_path
        report_file = Path(self.test_dir) / "report.json"
        
        result = self.reporter.generate_and_save_report(
            str(metrics_file),
            str(report_file)
        )
        assert result is True
        assert report_file.exists()
        
        # Step 5: Validate report
        with open(report_file, 'r') as f:
            report = json.load(f)
            assert 'time_window' in report
            assert report['time_window']['sample_count'] == 3
            assert 'cpu_analysis' in report
            assert 'memory_analysis' in report
    
    def test_continuous_collection(self):
        """Test continuous metric collection"""
        collection_count = 5
        
        for i in range(collection_count):
            metric = self.collector.collect_all_metrics()
            self.storage.write_metric(metric)
            if i < collection_count - 1:
                time.sleep(0.1)
        
        # Verify all metrics were stored
        stored_metrics = self.storage.read_metrics()
        assert len(stored_metrics) == collection_count
        
        # Verify timestamps are increasing
        timestamps = [m['timestamp'] for m in stored_metrics]
        assert timestamps == sorted(timestamps)
    
    def test_data_integrity(self):
        """Test data integrity through the pipeline"""
        # Collect original metric
        original_metric = self.collector.collect_all_metrics()
        
        # Store it
        self.storage.write_metric(original_metric)
        
        # Read it back
        stored_metrics = self.storage.read_metrics()
        assert len(stored_metrics) == 1
        
        retrieved_metric = stored_metrics[0]
        
        # Verify all fields are preserved
        assert retrieved_metric['timestamp'] == original_metric['timestamp']
        assert retrieved_metric['cpu'] == original_metric['cpu']
        assert retrieved_metric['memory'] == original_metric['memory']
        assert retrieved_metric['disk'] == original_metric['disk']
        assert retrieved_metric['network'] == original_metric['network']
    
    def test_batch_operations(self):
        """Test batch collection and storage"""
        # Collect batch of metrics
        batch_size = 10
        metrics_batch = []
        
        for _ in range(batch_size):
            metric = self.collector.collect_all_metrics()
            metrics_batch.append(metric)
            time.sleep(0.05)
        
        # Store batch
        written_count = self.storage.write_metrics_batch(metrics_batch)
        assert written_count == batch_size
        
        # Generate report from batch
        report = self.reporter.generate_summary_report(metrics_batch)
        assert report['time_window']['sample_count'] == batch_size
    
    def test_report_accuracy(self):
        """Test that report calculations are accurate"""
        # Create controlled test data
        test_metrics = [
            {
                "timestamp": 1000,
                "cpu": {"total": 10.0, "per_core": [10.0]},
                "memory": {"total": 1000, "used": 100, "free": 900, "available": 900},
                "disk": {"test": {"total": 1000, "used": 100, "free": 900}},
                "network": {"test": {"bytes_sent": 100, "bytes_recv": 200}}
            },
            {
                "timestamp": 1001,
                "cpu": {"total": 20.0, "per_core": [20.0]},
                "memory": {"total": 1000, "used": 200, "free": 800, "available": 800},
                "disk": {"test": {"total": 1000, "used": 200, "free": 800}},
                "network": {"test": {"bytes_sent": 150, "bytes_recv": 250}}
            },
            {
                "timestamp": 1002,
                "cpu": {"total": 30.0, "per_core": [30.0]},
                "memory": {"total": 1000, "used": 300, "free": 700, "available": 700},
                "disk": {"test": {"total": 1000, "used": 300, "free": 700}},
                "network": {"test": {"bytes_sent": 200, "bytes_recv": 300}}
            }
        ]
        
        # Generate report
        report = self.reporter.generate_summary_report(test_metrics)
        
        # Verify CPU average: (10+20+30)/3 = 20.0
        assert report['cpu_analysis']['total']['average'] == 20.0
        assert report['cpu_analysis']['total']['min'] == 10.0
        assert report['cpu_analysis']['total']['max'] == 30.0
        
        # Verify memory average: (100+200+300)/3 = 200.0
        assert report['memory_analysis']['used']['average_mb'] == 200.0
        
        # Verify network deltas
        assert report['network_analysis']['test']['delta_bytes_sent'] == 100  # 200-100
        assert report['network_analysis']['test']['delta_bytes_recv'] == 100  # 300-200
    
    def test_error_handling(self):
        """Test system handles errors gracefully"""
        # Test with invalid storage path (should not crash)
        # This test ensures robustness
        
        # Collect valid metric
        metric = self.collector.collect_all_metrics()
        assert metric is not None
        assert 'timestamp' in metric
        
        # Reporter should handle empty metrics gracefully
        empty_report = self.reporter.generate_summary_report([])
        assert 'error' in empty_report
    
    def test_concurrent_writes(self):
        """Test multiple writes in quick succession"""
        write_count = 20
        
        for i in range(write_count):
            metric = self.collector.collect_all_metrics()
            self.storage.write_metric(metric)
        
        # Verify all writes succeeded
        file_info = self.storage.get_file_info()
        assert file_info['record_count'] == write_count
        
        # Verify all records are valid
        metrics = self.storage.read_metrics()
        assert len(metrics) == write_count
        
        for metric in metrics:
            assert 'timestamp' in metric
            assert 'cpu' in metric
            assert 'memory' in metric


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
