#!/usr/bin/env python3
"""
Unit tests for collector.py
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from collector import MetricsCollector


class TestMetricsCollector:
    """Test suite for MetricsCollector"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.collector = MetricsCollector()
    
    def test_collector_initialization(self):
        """Test collector initializes properly"""
        assert self.collector is not None
        assert hasattr(self.collector, 'logger')
    
    def test_collect_cpu_metrics(self):
        """Test CPU metrics collection"""
        cpu_metrics = self.collector.collect_cpu_metrics()
        
        assert 'total' in cpu_metrics
        assert 'per_core' in cpu_metrics
        assert isinstance(cpu_metrics['total'], (int, float))
        assert isinstance(cpu_metrics['per_core'], list)
        assert 0 <= cpu_metrics['total'] <= 100
        
        for core_usage in cpu_metrics['per_core']:
            assert isinstance(core_usage, (int, float))
            assert 0 <= core_usage <= 100
    
    def test_collect_memory_metrics(self):
        """Test memory metrics collection"""
        mem_metrics = self.collector.collect_memory_metrics()
        
        assert 'total' in mem_metrics
        assert 'used' in mem_metrics
        assert 'free' in mem_metrics
        assert 'available' in mem_metrics
        
        # All values should be non-negative
        assert mem_metrics['total'] >= 0
        assert mem_metrics['used'] >= 0
        assert mem_metrics['free'] >= 0
        assert mem_metrics['available'] >= 0
        
        # Used + free should approximately equal total (with some tolerance)
        # Note: On some systems this might not be exact
        assert mem_metrics['used'] <= mem_metrics['total']
    
    def test_collect_disk_metrics(self):
        """Test disk metrics collection"""
        disk_metrics = self.collector.collect_disk_metrics()
        
        assert isinstance(disk_metrics, dict)
        
        # Should have at least one partition
        assert len(disk_metrics) > 0
        
        for partition, stats in disk_metrics.items():
            assert 'total' in stats
            assert 'used' in stats
            assert 'free' in stats
            
            # All values should be non-negative
            assert stats['total'] >= 0
            assert stats['used'] >= 0
            assert stats['free'] >= 0
            
            # Used should not exceed total
            assert stats['used'] <= stats['total']
    
    def test_collect_network_metrics(self):
        """Test network metrics collection"""
        net_metrics = self.collector.collect_network_metrics()
        
        assert isinstance(net_metrics, dict)
        
        for interface, stats in net_metrics.items():
            assert 'bytes_sent' in stats
            assert 'bytes_recv' in stats
            
            # All values should be non-negative
            assert stats['bytes_sent'] >= 0
            assert stats['bytes_recv'] >= 0
    
    def test_collect_all_metrics(self):
        """Test collecting all metrics together"""
        all_metrics = self.collector.collect_all_metrics()
        
        assert 'timestamp' in all_metrics
        assert 'cpu' in all_metrics
        assert 'memory' in all_metrics
        assert 'disk' in all_metrics
        assert 'network' in all_metrics
        
        # Timestamp should be a positive integer
        assert isinstance(all_metrics['timestamp'], int)
        assert all_metrics['timestamp'] > 0
        
        # Verify structure of each metric type
        assert 'total' in all_metrics['cpu']
        assert 'total' in all_metrics['memory']
        assert isinstance(all_metrics['disk'], dict)
        assert isinstance(all_metrics['network'], dict)
    
    def test_metrics_data_types(self):
        """Test that metrics have correct data types"""
        metrics = self.collector.collect_all_metrics()
        
        # CPU
        assert isinstance(metrics['cpu']['total'], (int, float))
        assert isinstance(metrics['cpu']['per_core'], list)
        
        # Memory
        assert isinstance(metrics['memory']['total'], int)
        assert isinstance(metrics['memory']['used'], int)
        
        # Disk
        for partition_stats in metrics['disk'].values():
            assert isinstance(partition_stats['total'], int)
            assert isinstance(partition_stats['used'], int)
        
        # Network
        for interface_stats in metrics['network'].values():
            assert isinstance(interface_stats['bytes_sent'], int)
            assert isinstance(interface_stats['bytes_recv'], int)
    
    def test_multiple_collections(self):
        """Test that multiple collections work correctly"""
        metrics1 = self.collector.collect_all_metrics()
        metrics2 = self.collector.collect_all_metrics()
        
        # Timestamps should be different (or very close)
        assert metrics1['timestamp'] <= metrics2['timestamp']
        
        # Both should have same structure
        assert metrics1.keys() == metrics2.keys()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
