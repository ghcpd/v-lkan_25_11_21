@echo off
REM End-to-end demonstration script for Windows

echo ==========================================
echo METRICS COLLECTION FRAMEWORK - DEMO
echo ==========================================
echo.

REM Step 1: Setup
echo Step 1: Setting up environment...
if not exist "venv" (
    call setup.bat
) else (
    echo Environment already set up
    call venv\Scripts\activate.bat
)
echo.

REM Step 2: Run tests
echo Step 2: Running automated tests...
python run_tests.py
set TEST_EXIT_CODE=%ERRORLEVEL%
echo.

REM Step 3: Collect metrics
echo Step 3: Collecting system metrics (15 seconds)...
python main.py --mode collect --duration 15
echo.

REM Step 4: Generate report
echo Step 4: Generating summary report...
python main.py --mode report
echo.

REM Step 5: Display results
echo Step 5: Displaying results...
echo.

if exist "data\metrics.jsonl" (
    echo Metrics file (first 5 lines):
    echo ----------------------------
    powershell -Command "Get-Content data\metrics.jsonl -Head 5"
    echo.
)

if exist "data\summary.json" (
    echo Summary report:
    echo ----------------------------
    type data\summary.json
    echo.
)

REM Step 6: Show test results
if exist "test_reports\test_report_latest.json" (
    echo Test Results Summary:
    echo ----------------------------
    python -c "import json; report = json.load(open('test_reports/test_report_latest.json')); print(f\"Total Tests: {report['test_run']['total_tests']}\"); print(f\"Passed: {report['test_run']['passed']}\"); print(f\"Failed: {report['test_run']['failed']}\"); print(f\"Python Version: {report['test_run']['python_version']}\"); print(f\"System: {report['system_info']['os']}\"); print(f\"CPUs: {report['system_info']['cpu_count']}\"); print(f\"Memory: {report['system_info']['total_memory_mb']} MB\")"
    echo.
)

echo ==========================================
echo DEMO COMPLETE!
echo ==========================================
echo.
echo Generated files:
echo   - data\metrics.jsonl       (collected metrics)
echo   - data\summary.json        (summary report)
echo   - test_reports\            (test results)
echo   - metrics_app.log          (application logs)
echo.
echo To run custom collection:
echo   python main.py --mode collect --duration 60
echo.
echo To generate custom report:
echo   python main.py --mode report --output my_report.json
echo.

pause
exit /b %TEST_EXIT_CODE%
