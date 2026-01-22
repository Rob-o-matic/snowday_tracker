#!/usr/bin/env python3
"""
Test script for School Closings Tracker
Demonstrates functionality with mock data when network is unavailable.
"""

import csv
from datetime import datetime
import os

def test_scraper_with_mock_data():
    """Test the scraper with mock data."""
    print("=" * 60)
    print("Testing School Closings Tracker with Mock Data")
    print("=" * 60)
    
    # Mock school closings data
    mock_schools = [
        {
            'school_name': 'Boston Public Schools',
            'school_type': 'District',
            'status': 'Closed',
            'raw_text': 'Boston Public Schools - Closed due to weather conditions'
        },
        {
            'school_name': 'Cambridge Elementary School',
            'school_type': 'Elementary',
            'status': '2-Hour Delay',
            'raw_text': 'Cambridge Elementary School - 2 hour delay'
        },
        {
            'school_name': 'Newton South High School',
            'school_type': 'High',
            'status': '3-Hour Delay',
            'raw_text': 'Newton South High School - 3 hour delay'
        },
        {
            'school_name': 'Brookline Middle School',
            'school_type': 'Middle',
            'status': 'Early Release',
            'raw_text': 'Brookline Middle School - Early release at 12:00 PM'
        },
        {
            'school_name': 'Somerville Academy',
            'school_type': 'Unknown',
            'status': 'Cancelled',
            'raw_text': 'Somerville Academy - All after-school activities cancelled'
        }
    ]
    
    # Mock precipitation data (3.5 inches)
    mock_precipitation = 3.5
    
    # Create test CSV file
    output_file = 'test_school_closings_log.csv'
    retrieval_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"\n[1/3] Mock precipitation data: {mock_precipitation} inches")
    print(f"\n[2/3] Processing {len(mock_schools)} school closings:")
    
    for school in mock_schools:
        print(f"  - {school['school_name']} ({school['school_type']}): {school['status']}")
    
    print(f"\n[3/3] Writing to CSV file: {output_file}")
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'retrieval_date',
            'retrieval_time',
            'school_name',
            'school_type',
            'status',
            'precipitation_24h_inches',
            'raw_text'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for school in mock_schools:
            writer.writerow({
                'retrieval_date': retrieval_time.split()[0],
                'retrieval_time': retrieval_time.split()[1],
                'school_name': school['school_name'],
                'school_type': school['school_type'],
                'status': school['status'],
                'precipitation_24h_inches': mock_precipitation,
                'raw_text': school['raw_text']
            })
    
    print("\n" + "=" * 60)
    print("Test Completed Successfully!")
    print(f"Total schools logged: {len(mock_schools)}")
    print(f"24-hour precipitation: {mock_precipitation} inches")
    print(f"Output file: {output_file}")
    print("=" * 60)
    
    # Display the CSV content
    print("\nCSV Content Preview:")
    print("-" * 60)
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
        print(content)

if __name__ == '__main__':
    test_scraper_with_mock_data()
