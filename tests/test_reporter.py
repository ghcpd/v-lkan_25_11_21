#!/usr/bin/env python3
"""
Unit tests for reporter.py
"""

import pytest
import json
import sys
from pathlib import Path
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from reporter import MetricsReporter


class TestMetricsReporter:
    """Test suite for MetricsReporter"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.reporter = MetricsReporter()
        self.test_dir = tempfile.mkdtemp()
        
        # Create sample metrics
        self.sample_metrics = [
            {
                "timestamp": 1000,
                "cpu": {"total": 30.0, "per_core": [25.0, 35.0]},
                "memory": {"total": 8192, "used": 4000, "free": 4192, "available": 4192},
                "disk": {"C:": {"total": 512000, "used": 256000, "free": 256000}},
                "network": {"eth0": {"bytes_sent": 1000, "bytes_recv": 2000}}
            },
            {
                "timestamp": 1005,
                "cpu": {"total": 40.0, "per_core": [35.0, 45.0]},
                "memory": {"total": 8192, "used": 4500, "free": 3692, "available": 3692},
                "disk": {"C:": {"total": 512000, "used": 257000, "free": 255000}},
                "network": {"eth0": {"bytes_sent": 1500, "bytes_recv": 2500}}
            },
            {
                "timestamp": 1010,
                "cpu": {"total": 35.0, "per_core": [30.0, 40.0]},
                "memory": {"total": 8192, "used": 4200, "free": 3992, "available": 3992},
                "disk": {"C:": {"total": 512000, "used": 258000, "free": 254000}},
                "network": {"eth0": {"bytes_sent": 2000, "bytes_recv": 3000}}
            }
        ]
    
    def teardown_method(self):
        """Cleanup test fixtures"""
        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)
    
    def test_reporter_initialization(self):
        """Test reporter initializes properly"""
        assert self.reporter is not None
        assert hasattr(self.reporter, 'logger')
    
    def test_analyze_cpu_metrics(self):
        """Test CPU metrics analysis"""
        analysis = self.reporter.analyze_cpu_metrics(self.sample_metrics)
        
        assert 'total' in analysis
        assert 'per_core' in analysis
        
        # Check total CPU stats
        assert 'average' in analysis['total']
        assert 'median' in analysis['total']
        assert 'min' in analysis['total']
        assert 'max' in analysis['total']
        assert 'samples' in analysis['total']
        
        # Verify calculations
        assert analysis['total']['average'] == 35.0  # (30+40+35)/3
        assert analysis['total']['median'] == 35.0
        assert analysis['total']['min'] == 30.0
        assert analysis['total']['max'] == 40.0
        assert analysis['total']['samples'] == 3
        
        # Check per-core stats
        assert 'core_0' in analysis['per_core']
        assert 'core_1' in analysis['per_core']
    
    def test_analyze_memory_metrics(self):
        """Test memory metrics analysis"""
        analysis = self.reporter.analyze_memory_metrics(self.sample_metrics)
        
        assert 'total_mb' in analysis
        assert 'used' in analysis
        assert 'available' in analysis
        assert 'samples' in analysis
        
        assert analysis['total_mb'] == 8192
        assert analysis['samples'] == 3
        
        # Check used memory stats
        assert 'average_mb' in analysis['used']
        assert 'min_mb' in analysis['used']
        assert 'max_mb' in analysis['used']
        
        # Verify calculations
        expected_avg = round((4000 + 4500 + 4200) / 3, 2)
        assert analysis['used']['average_mb'] == expected_avg
        assert analysis['used']['min_mb'] == 4000
        assert analysis['used']['max_mb'] == 4500
    
    def test_analyze_disk_metrics(self):
        """Test disk metrics analysis"""
        analysis = self.reporter.analyze_disk_metrics(self.sample_metrics)
        
        assert 'C:' in analysis
        
        partition_stats = analysis['C:']
        assert 'total_mb' in partition_stats
        assert 'used' in partition_stats
        assert 'free' in partition_stats
        
        assert partition_stats['total_mb'] == 512000
        
        # Check used disk stats
        assert 'average_mb' in partition_stats['used']
        assert partition_stats['used']['min_mb'] == 256000
        assert partition_stats['used']['max_mb'] == 258000
    
    def test_analyze_network_metrics(self):
        """Test network metrics analysis"""
        analysis = self.reporter.analyze_network_metrics(self.sample_metrics)
        
        assert 'eth0' in analysis
        
        interface_stats = analysis['eth0']
        assert 'total_bytes_sent' in interface_stats
        assert 'total_bytes_recv' in interface_stats
        assert 'delta_bytes_sent' in interface_stats
        assert 'delta_bytes_recv' in interface_stats
        assert 'samples' in interface_stats
        
        # Verify deltas (last - first)
        assert interface_stats['delta_bytes_sent'] == 1000  # 2000 - 1000
        assert interface_stats['delta_bytes_recv'] == 1000  # 3000 - 2000
        assert interface_stats['samples'] == 3
    
    def test_generate_summary_report(self):
        """Test generating complete summary report"""
        report = self.reporter.generate_summary_report(self.sample_metrics)
        
        assert 'generated_at' in report
        assert 'time_window' in report
        assert 'cpu_analysis' in report
        assert 'memory_analysis' in report
        assert 'disk_analysis' in report
        assert 'network_analysis' in report
        
        # Check time window
        assert report['time_window']['start'] == 1000
        assert report['time_window']['end'] == 1010
        assert report['time_window']['duration_seconds'] == 10
        assert report['time_window']['sample_count'] == 3
    
    def test_generate_report_empty_metrics(self):
        """Test report generation with empty metrics"""
        report = self.reporter.generate_summary_report([])
        assert 'error' in report
    
    def test_save_report(self):
        """Test saving report to file"""
        report = self.reporter.generate_summary_report(self.sample_metrics)
        output_path = Path(self.test_dir) / "test_report.json"
        
        result = self.reporter.save_report(report, str(output_path))
        assert result is True
        assert output_path.exists()
        
        # Verify content
        with open(output_path, 'r') as f:
            loaded_report = json.load(f)
            assert loaded_report == report
    
    def test_load_metrics_from_file(self):
        """Test loading metrics from JSONL file"""
        # Create test JSONL file
        test_file = Path(self.test_dir) / "test_metrics.jsonl"
        
        with open(test_file, 'w') as f:
            for metric in self.sample_metrics:
                f.write(json.dumps(metric) + '\n')
        
        # Load metrics
        loaded_metrics = self.reporter.load_metrics_from_file(str(test_file))
        assert len(loaded_metrics) == 3
        assert loaded_metrics == self.sample_metrics
    
    def test_load_nonexistent_file(self):
        """Test loading from non-existent file"""
        metrics = self.reporter.load_metrics_from_file("nonexistent.jsonl")
        assert metrics == []
    
    def test_generate_and_save_report(self):
        """Test end-to-end report generation"""
        # Create test JSONL file
        test_file = Path(self.test_dir) / "metrics.jsonl"
        with open(test_file, 'w') as f:
            for metric in self.sample_metrics:
                f.write(json.dumps(metric) + '\n')
        
        # Generate and save report
        output_file = Path(self.test_dir) / "report.json"
        result = self.reporter.generate_and_save_report(
            str(test_file),
            str(output_file)
        )
        
        assert result is True
        assert output_file.exists()
        
        # Verify report content
        with open(output_file, 'r') as f:
            report = json.load(f)
            assert 'cpu_analysis' in report
            assert 'memory_analysis' in report
    
    def test_report_structure_validation(self):
        """Test that generated report has correct structure"""
        report = self.reporter.generate_summary_report(self.sample_metrics)
        
        # Validate time_window structure
        assert isinstance(report['time_window']['start'], int)
        assert isinstance(report['time_window']['end'], int)
        assert isinstance(report['time_window']['duration_seconds'], int)
        assert isinstance(report['time_window']['sample_count'], int)
        
        # Validate CPU analysis structure
        assert isinstance(report['cpu_analysis']['total']['average'], float)
        assert isinstance(report['cpu_analysis']['per_core'], dict)
        
        # Validate memory analysis structure
        assert isinstance(report['memory_analysis']['total_mb'], int)
        assert isinstance(report['memory_analysis']['used']['average_mb'], float)
        
        # Report should be JSON serializable
        json_str = json.dumps(report)
        assert isinstance(json_str, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
