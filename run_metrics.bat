@echo off
REM Script to run metrics collection on Windows

echo Starting Metrics Collection...

REM Activate virtual environment if exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Default duration 30 seconds
set DURATION=30
if not "%1"=="" set DURATION=%1

echo Collection will run for %DURATION% seconds
echo Press Ctrl+C to stop early
echo.

REM Run metrics collection
python main.py --mode collect --duration %DURATION%

echo.
echo Collection complete!
echo Metrics saved to data\metrics.jsonl
pause
