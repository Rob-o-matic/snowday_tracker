#!/bin/bash
# Test runner script for School Closings Tracker

set -e

echo "======================================"
echo "School Closings Tracker - Test Runner"
echo "======================================"
echo ""

# Check if pytest is installed
if ! python3 -c "import pytest" &> /dev/null
then
    echo "Installing test dependencies..."
    pip install -r requirements.txt
    echo ""
fi

# Run tests
echo "Running unit tests..."
python3 -m pytest tests/ -v --tb=short

echo ""
echo "======================================"
echo "All tests completed!"
echo "======================================"
