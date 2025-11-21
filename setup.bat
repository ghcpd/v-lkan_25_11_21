@echo off
REM Setup script for Windows environment

echo Setting up Metrics Collection Framework...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.8 or higher.
    exit /b 1
)

echo Python check passed
echo.

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create directories
if not exist "data" mkdir data
if not exist "test_reports" mkdir test_reports

echo.
echo ==========================================
echo Setup complete!
echo ==========================================
echo.
echo To activate the environment:
echo   venv\Scripts\activate.bat
echo.
echo To run metrics collection:
echo   python main.py --mode collect --duration 30
echo.
echo To run tests:
echo   python run_tests.py
echo.
echo To generate a report:
echo   python main.py --mode report
echo.
pause
