#!/bin/bash
# Simple runner script for the school closings tracker

echo "======================================"
echo "School Closings Tracker Runner"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if dependencies are installed
if ! python3 -c "import requests" &> /dev/null
then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

# Run the scraper
echo "Running school closings scraper..."
echo ""
python3 school_closings_scraper.py

echo ""
echo "======================================"
echo "Done! Check school_closings_log.csv for results"
echo "======================================"
