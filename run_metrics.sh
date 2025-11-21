#!/bin/bash

# Script to run metrics collection
echo "Starting Metrics Collection..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Default parameters
DURATION=${1:-30}  # Default 30 seconds

echo "Collection will run for $DURATION seconds"
echo "Press Ctrl+C to stop early"
echo ""

# Run metrics collection
python main.py --mode collect --duration $DURATION

echo ""
echo "Collection complete!"
echo "Metrics saved to data/metrics.jsonl"
