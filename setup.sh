#!/bin/bash

# Setup script for local environment
echo "Setting up Metrics Collection Framework..."

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.8 or higher is required. Found: $python_version"
    exit 1
fi

echo "Python version check passed: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create data directory
if [ ! -d "data" ]; then
    echo "Creating data directory..."
    mkdir -p data
fi

# Create test reports directory
if [ ! -d "test_reports" ]; then
    echo "Creating test reports directory..."
    mkdir -p test_reports
fi

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "To activate the environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run metrics collection:"
echo "  python main.py --mode collect --duration 30"
echo ""
echo "To run tests:"
echo "  pytest tests/ -v"
echo ""
echo "To generate a report:"
echo "  python main.py --mode report"
echo ""
