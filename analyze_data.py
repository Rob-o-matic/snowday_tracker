#!/usr/bin/env python3
"""
Example analysis script for school closings data.
Demonstrates how to read and analyze the CSV log file.
"""

import csv
from collections import Counter
from datetime import datetime

def analyze_school_closings(csv_file='school_closings_log.csv'):
    """
    Analyze school closings data from CSV file.
    Shows summary statistics and insights.
    """
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            records = list(reader)
        
        if not records:
            print("No records found in CSV file.")
            return
        
        print("=" * 60)
        print("SCHOOL CLOSINGS DATA ANALYSIS")
        print("=" * 60)
        print(f"\nTotal records: {len(records)}")
        
        # Count by status
        status_counts = Counter(record['status'] for record in records)
        print("\n📊 Closings/Delays by Status:")
        for status, count in status_counts.most_common():
            print(f"  {status}: {count}")
        
        # Count by school type
        type_counts = Counter(record['school_type'] for record in records)
        print("\n🏫 Closings/Delays by School Type:")
        for school_type, count in type_counts.most_common():
            print(f"  {school_type}: {count}")
        
        # Precipitation stats
        precip_values = []
        for record in records:
            try:
                precip = float(record['precipitation_24h_inches'])
                precip_values.append(precip)
            except (ValueError, KeyError):
                pass
        
        if precip_values:
            avg_precip = sum(precip_values) / len(precip_values)
            max_precip = max(precip_values)
            min_precip = min(precip_values)
            
            print("\n🌧️  Precipitation Statistics (24-hour totals):")
            print(f"  Average: {avg_precip:.2f} inches")
            print(f"  Maximum: {max_precip:.2f} inches")
            print(f"  Minimum: {min_precip:.2f} inches")
        
        # Date range
        dates = [record['retrieval_date'] for record in records if record.get('retrieval_date')]
        if dates:
            unique_dates = sorted(set(dates))
            print(f"\n📅 Data covers {len(unique_dates)} day(s):")
            print(f"  First: {unique_dates[0]}")
            print(f"  Last: {unique_dates[-1]}")
        
        # Top schools with closings
        school_counts = Counter(record['school_name'] for record in records 
                               if record['school_name'] != 'NO_CLOSINGS_FOUND')
        if school_counts:
            print("\n🎓 Schools with most closings/delays:")
            for school, count in school_counts.most_common(5):
                print(f"  {school}: {count}")
        
        print("\n" + "=" * 60)
        print("Analysis complete!")
        print("=" * 60)
        
    except FileNotFoundError:
        print(f"Error: File '{csv_file}' not found.")
        print("Run the scraper first to generate data.")
    except Exception as e:
        print(f"Error analyzing data: {e}")

if __name__ == '__main__':
    analyze_school_closings()
