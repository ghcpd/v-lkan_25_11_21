#!/usr/bin/env python3
"""
Test runner script that generates test report
"""

import json
import sys
import subprocess
import platform
from datetime import datetime
from pathlib import Path


def run_pytest():
    """Run pytest and capture results"""
    print("Running pytest...")
    
    # Run pytest with JSON report
    result = subprocess.run(
        ['pytest', 'tests/', '-v', '--tb=short', '--json-report', '--json-report-file=test_output.json'],
        capture_output=True,
        text=True
    )
    
    return result


def generate_test_report(pytest_result):
    """Generate test report from pytest results"""
    
    # Load template
    template_path = Path('test_report_template.json')
    with open(template_path, 'r') as f:
        report = json.load(f)
    
    # Parse pytest output
    output_lines = pytest_result.stdout.split('\n')
    
    # Extract test counts from pytest output
    for line in output_lines:
        if 'passed' in line or 'failed' in line:
            # Parse summary line
            parts = line.split()
            for i, part in enumerate(parts):
                if 'passed' in part and i > 0:
                    try:
                        report['test_run']['passed'] = int(parts[i-1])
                    except (ValueError, IndexError):
                        pass
                if 'failed' in part and i > 0:
                    try:
                        report['test_run']['failed'] = int(parts[i-1])
                    except (ValueError, IndexError):
                        pass
    
    # Update report metadata
    report['test_run']['timestamp'] = datetime.now().isoformat()
    report['test_run']['python_version'] = platform.python_version()
    report['test_run']['total_tests'] = report['test_run']['passed'] + report['test_run']['failed']
    
    # System info
    import psutil
    report['system_info']['os'] = platform.system()
    report['system_info']['cpu_count'] = psutil.cpu_count()
    report['system_info']['total_memory_mb'] = psutil.virtual_memory().total // (1024 * 1024)
    
    # Parse test suites
    test_suites = {
        'test_collector.py': {'name': 'Collector Tests', 'tests': []},
        'test_storage.py': {'name': 'Storage Tests', 'tests': []},
        'test_reporter.py': {'name': 'Reporter Tests', 'tests': []},
        'test_integration.py': {'name': 'Integration Tests', 'tests': []}
    }
    
    current_suite = None
    for line in output_lines:
        if 'test_' in line and ('PASSED' in line or 'FAILED' in line):
            # Extract test name
            if '::' in line:
                parts = line.split('::')
                if len(parts) >= 2:
                    suite_name = parts[0].split('/')[-1]
                    test_name = parts[-1].split()[0]
                    status = 'PASSED' if 'PASSED' in line else 'FAILED'
                    
                    if suite_name in test_suites:
                        test_suites[suite_name]['tests'].append({
                            'name': test_name,
                            'status': status
                        })
                        
                        if status == 'FAILED':
                            report['failed_tests'].append({
                                'suite': suite_name,
                                'test': test_name
                            })
    
    # Add suites to report
    for suite_name, suite_data in test_suites.items():
        if suite_data['tests']:
            passed = sum(1 for t in suite_data['tests'] if t['status'] == 'PASSED')
            failed = sum(1 for t in suite_data['tests'] if t['status'] == 'FAILED')
            
            report['test_suites'].append({
                'name': suite_data['name'],
                'file': suite_name,
                'total_tests': len(suite_data['tests']),
                'passed': passed,
                'failed': failed,
                'tests': suite_data['tests']
            })
    
    return report


def main():
    """Main function"""
    print("="*60)
    print("METRICS FRAMEWORK - TEST SUITE")
    print("="*60)
    print()
    
    # Run pytest
    pytest_result = run_pytest()
    
    # Generate report
    print("\nGenerating test report...")
    report = generate_test_report(pytest_result)
    
    # Save report
    report_path = Path('test_reports') / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Also save as latest
    latest_path = Path('test_reports') / 'test_report_latest.json'
    with open(latest_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total Tests: {report['test_run']['total_tests']}")
    print(f"Passed: {report['test_run']['passed']}")
    print(f"Failed: {report['test_run']['failed']}")
    print(f"Success Rate: {(report['test_run']['passed']/report['test_run']['total_tests']*100):.1f}%" if report['test_run']['total_tests'] > 0 else "N/A")
    print()
    print(f"Report saved to: {report_path}")
    print(f"Latest report: {latest_path}")
    print("="*60)
    
    # Print pytest output
    print("\nDetailed Output:")
    print(pytest_result.stdout)
    
    if pytest_result.stderr:
        print("\nErrors:")
        print(pytest_result.stderr)
    
    # Return exit code
    return pytest_result.returncode


if __name__ == "__main__":
    sys.exit(main())
