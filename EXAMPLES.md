# Example Outputs

## Sample JSONL Record

A single line from `data/metrics.jsonl`:

```json
{"timestamp": 1700580000, "cpu": {"total": 42.5, "per_core": [35.2, 48.9, 41.3, 44.6, 39.8, 45.2, 40.1, 43.7]}, "memory": {"total": 16384, "used": 9216, "free": 2048, "available": 7168}, "disk": {"C:\\": {"total": 512000, "used": 358400, "free": 153600}, "D:\\": {"total": 1024000, "used": 512000, "free": 512000}}, "network": {"Ethernet": {"bytes_sent": 152843976, "bytes_recv": 892764532}, "Wi-Fi": {"bytes_sent": 45632189, "bytes_recv": 234567890}}}
```

Formatted for readability:

```json
{
  "timestamp": 1700580000,
  "cpu": {
    "total": 42.5,
    "per_core": [35.2, 48.9, 41.3, 44.6, 39.8, 45.2, 40.1, 43.7]
  },
  "memory": {
    "total": 16384,
    "used": 9216,
    "free": 2048,
    "available": 7168
  },
  "disk": {
    "C:\\": {
      "total": 512000,
      "used": 358400,
      "free": 153600
    },
    "D:\\": {
      "total": 1024000,
      "used": 512000,
      "free": 512000
    }
  },
  "network": {
    "Ethernet": {
      "bytes_sent": 152843976,
      "bytes_recv": 892764532
    },
    "Wi-Fi": {
      "bytes_sent": 45632189,
      "bytes_recv": 234567890
    }
  }
}
```

## Sample Summary Report

Contents of `data/summary.json`:

```json
{
  "generated_at": 1700580300,
  "time_window": {
    "start": 1700580000,
    "end": 1700580300,
    "duration_seconds": 300,
    "sample_count": 60
  },
  "cpu_analysis": {
    "total": {
      "average": 38.75,
      "median": 37.5,
      "min": 15.2,
      "max": 68.9,
      "samples": 60
    },
    "per_core": {
      "core_0": {
        "average": 35.4,
        "min": 12.0,
        "max": 65.3
      },
      "core_1": {
        "average": 42.1,
        "min": 18.5,
        "max": 72.4
      },
      "core_2": {
        "average": 36.8,
        "min": 14.2,
        "max": 64.1
      },
      "core_3": {
        "average": 40.5,
        "min": 16.8,
        "max": 69.7
      }
    }
  },
  "memory_analysis": {
    "total_mb": 16384,
    "used": {
      "average_mb": 9012.34,
      "min_mb": 8456,
      "max_mb": 9876
    },
    "available": {
      "average_mb": 7371.66,
      "min_mb": 6508,
      "max_mb": 7928
    },
    "samples": 60
  },
  "disk_analysis": {
    "C:\\": {
      "total_mb": 512000,
      "used": {
        "average_mb": 358420.5,
        "min_mb": 358400,
        "max_mb": 358450
      },
      "free": {
        "average_mb": 153579.5,
        "min_mb": 153550,
        "max_mb": 153600
      }
    },
    "D:\\": {
      "total_mb": 1024000,
      "used": {
        "average_mb": 512015.3,
        "min_mb": 512000,
        "max_mb": 512100
      },
      "free": {
        "average_mb": 511984.7,
        "min_mb": 511900,
        "max_mb": 512000
      }
    }
  },
  "network_analysis": {
    "Ethernet": {
      "total_bytes_sent": 153456789,
      "total_bytes_recv": 894567890,
      "delta_bytes_sent": 612813,
      "delta_bytes_recv": 1803358,
      "samples": 60
    },
    "Wi-Fi": {
      "total_bytes_sent": 45678901,
      "total_bytes_recv": 235678901,
      "delta_bytes_sent": 46712,
      "delta_bytes_recv": 1111011,
      "samples": 60
    }
  }
}
```

## Sample Test Report

Contents of `test_reports/test_report_latest.json`:

```json
{
  "test_run": {
    "timestamp": "2025-11-21T14:30:45.123456",
    "framework": "pytest",
    "python_version": "3.11.5",
    "total_tests": 49,
    "passed": 49,
    "failed": 0,
    "skipped": 0,
    "duration_seconds": 12.456
  },
  "test_suites": [
    {
      "name": "Collector Tests",
      "file": "test_collector.py",
      "total_tests": 15,
      "passed": 15,
      "failed": 0,
      "tests": [
        {"name": "test_collector_initialization", "status": "PASSED"},
        {"name": "test_collect_cpu_metrics", "status": "PASSED"},
        {"name": "test_collect_memory_metrics", "status": "PASSED"},
        {"name": "test_collect_disk_metrics", "status": "PASSED"},
        {"name": "test_collect_network_metrics", "status": "PASSED"}
      ]
    },
    {
      "name": "Storage Tests",
      "file": "test_storage.py",
      "total_tests": 12,
      "passed": 12,
      "failed": 0,
      "tests": [
        {"name": "test_storage_initialization", "status": "PASSED"},
        {"name": "test_write_single_metric", "status": "PASSED"},
        {"name": "test_write_multiple_metrics", "status": "PASSED"},
        {"name": "test_read_metrics", "status": "PASSED"}
      ]
    },
    {
      "name": "Reporter Tests",
      "file": "test_reporter.py",
      "total_tests": 13,
      "passed": 13,
      "failed": 0,
      "tests": [
        {"name": "test_reporter_initialization", "status": "PASSED"},
        {"name": "test_analyze_cpu_metrics", "status": "PASSED"},
        {"name": "test_analyze_memory_metrics", "status": "PASSED"},
        {"name": "test_generate_summary_report", "status": "PASSED"}
      ]
    },
    {
      "name": "Integration Tests",
      "file": "test_integration.py",
      "total_tests": 9,
      "passed": 9,
      "failed": 0,
      "tests": [
        {"name": "test_end_to_end_workflow", "status": "PASSED"},
        {"name": "test_continuous_collection", "status": "PASSED"},
        {"name": "test_data_integrity", "status": "PASSED"}
      ]
    }
  ],
  "failed_tests": [],
  "coverage": {
    "total_statements": 0,
    "covered_statements": 0,
    "coverage_percentage": 0.0
  },
  "system_info": {
    "os": "Windows",
    "cpu_count": 8,
    "total_memory_mb": 16384
  }
}
```

## Console Output Examples

### Running Collection

```
$ python main.py --mode collect --duration 30

2025-11-21 14:30:00,123 - __main__ - INFO - Metrics application initialized
2025-11-21 14:30:00,125 - __main__ - INFO - Starting continuous metrics collection
2025-11-21 14:30:00,125 - __main__ - INFO - Collection interval: 5 seconds
2025-11-21 14:30:30,456 - __main__ - INFO - Duration limit of 30s reached
2025-11-21 14:30:30,457 - __main__ - INFO - Collection stopped. Total metrics collected: 6

============================================================
METRICS COLLECTION SUMMARY
============================================================
Metrics file: d:\Downloads\data\metrics.jsonl
File size: 0.03 MB (31,456 bytes)
Total records: 6
============================================================
```

### Running Tests

```
$ python run_tests.py

============================================================
METRICS FRAMEWORK - TEST SUITE
============================================================

Running pytest...

======================== test session starts ========================
collected 49 items

tests/test_collector.py::TestMetricsCollector::test_collector_initialization PASSED
tests/test_collector.py::TestMetricsCollector::test_collect_cpu_metrics PASSED
tests/test_collector.py::TestMetricsCollector::test_collect_memory_metrics PASSED
...
tests/test_integration.py::TestIntegration::test_end_to_end_workflow PASSED

======================== 49 passed in 12.45s ========================

Generating test report...

============================================================
TEST SUMMARY
============================================================
Total Tests: 49
Passed: 49
Failed: 0
Success Rate: 100.0%

Report saved to: test_reports/test_report_20251121_143045.json
Latest report: test_reports/test_report_latest.json
============================================================
```

### Generating Report

```
$ python main.py --mode report

2025-11-21 14:35:00,123 - __main__ - INFO - Metrics application initialized
2025-11-21 14:35:00,125 - reporter - INFO - Generating report from data\metrics.jsonl
2025-11-21 14:35:00,234 - reporter - INFO - Report saved to data\summary.json
2025-11-21 14:35:00,235 - __main__ - INFO - Report generated: data\summary.json
```
