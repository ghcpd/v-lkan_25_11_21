#!/bin/bash

# End-to-end demonstration script
echo "=========================================="
echo "METRICS COLLECTION FRAMEWORK - DEMO"
echo "=========================================="
echo ""

# Step 1: Setup
echo "Step 1: Setting up environment..."
if [ ! -d "venv" ]; then
    bash setup.sh
else
    echo "Environment already set up"
    source venv/bin/activate
fi
echo ""

# Step 2: Run tests
echo "Step 2: Running automated tests..."
python run_tests.py
TEST_EXIT_CODE=$?
echo ""

# Step 3: Collect metrics
echo "Step 3: Collecting system metrics (15 seconds)..."
python main.py --mode collect --duration 15
echo ""

# Step 4: Generate report
echo "Step 4: Generating summary report..."
python main.py --mode report
echo ""

# Step 5: Display results
echo "Step 5: Displaying results..."
echo ""

if [ -f "data/metrics.jsonl" ]; then
    echo "Metrics file (first 5 lines):"
    echo "----------------------------"
    head -5 data/metrics.jsonl | python -m json.tool 2>/dev/null || head -5 data/metrics.jsonl
    echo ""
fi

if [ -f "data/summary.json" ]; then
    echo "Summary report:"
    echo "----------------------------"
    cat data/summary.json | python -m json.tool 2>/dev/null || cat data/summary.json
    echo ""
fi

# Step 6: Show test results
if [ -f "test_reports/test_report_latest.json" ]; then
    echo "Test Results Summary:"
    echo "----------------------------"
    python -c "
import json
with open('test_reports/test_report_latest.json', 'r') as f:
    report = json.load(f)
    print(f\"Total Tests: {report['test_run']['total_tests']}\")
    print(f\"Passed: {report['test_run']['passed']}\")
    print(f\"Failed: {report['test_run']['failed']}\")
    print(f\"Python Version: {report['test_run']['python_version']}\")
    print(f\"System: {report['system_info']['os']}\")
    print(f\"CPUs: {report['system_info']['cpu_count']}\")
    print(f\"Memory: {report['system_info']['total_memory_mb']} MB\")
" 2>/dev/null
    echo ""
fi

echo "=========================================="
echo "DEMO COMPLETE!"
echo "=========================================="
echo ""
echo "Generated files:"
echo "  - data/metrics.jsonl       (collected metrics)"
echo "  - data/summary.json        (summary report)"
echo "  - test_reports/            (test results)"
echo "  - metrics_app.log          (application logs)"
echo ""
echo "To run custom collection:"
echo "  python main.py --mode collect --duration 60"
echo ""
echo "To generate custom report:"
echo "  python main.py --mode report --output my_report.json"
echo ""

exit $TEST_EXIT_CODE
