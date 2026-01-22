#!/usr/bin/env python3
"""
School Closings Tracker
Scrapes CBS Boston school closings website and logs closings/delays with precipitation data.
"""

import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SchoolClosingsScraper:
    """Scraper for CBS Boston school closings website."""
    
    def __init__(self):
        """Initialize the scraper with configuration."""
        load_dotenv()
        self.school_closings_url = "https://www.cbsnews.com/boston/school-closings/"
        self.weather_lat = os.getenv('WEATHER_LATITUDE', '42.3601')
        self.weather_lon = os.getenv('WEATHER_LONGITUDE', '-71.0589')
        self.output_file = 'school_closings_log.csv'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def fetch_precipitation_data(self):
        """
        Fetch 24-hour precipitation data from weather.gov API.
        Returns precipitation amount in inches.
        """
        try:
            # First, get the grid point data for the coordinates
            points_url = f"https://api.weather.gov/points/{self.weather_lat},{self.weather_lon}"
            logger.info(f"Fetching weather grid point data from: {points_url}")
            
            response = requests.get(points_url, headers={'User-Agent': 'SchoolClosingsTracker/1.0'}, timeout=10)
            response.raise_for_status()
            points_data = response.json()
            
            # Get the observations station URL
            observation_stations_url = points_data['properties']['observationStations']
            logger.info(f"Fetching observation stations from: {observation_stations_url}")
            
            response = requests.get(observation_stations_url, headers={'User-Agent': 'SchoolClosingsTracker/1.0'}, timeout=10)
            response.raise_for_status()
            stations_data = response.json()
            
            # Get the first (nearest) station
            if stations_data['features']:
                station_id = stations_data['features'][0]['properties']['stationIdentifier']
                logger.info(f"Using weather station: {station_id}")
                
                # Get observations from the station
                observations_url = f"https://api.weather.gov/stations/{station_id}/observations"
                logger.info(f"Fetching observations from: {observations_url}")
                
                response = requests.get(observations_url, headers={'User-Agent': 'SchoolClosingsTracker/1.0'}, timeout=10)
                response.raise_for_status()
                observations_data = response.json()
                
                # Calculate total precipitation from last 24 hours
                # Note: precipitationLastHour gives the precipitation for that specific hour
                # We sum all hourly values within the 24-hour window
                # This approach gives an approximation of total precipitation
                total_precipitation = 0.0
                current_time = datetime.now(timezone.utc)
                
                for observation in observations_data.get('features', []):
                    obs_time_str = observation['properties'].get('timestamp')
                    if obs_time_str:
                        obs_time = datetime.fromisoformat(obs_time_str.replace('Z', '+00:00'))
                        time_diff = (current_time - obs_time).total_seconds() / 3600
                        
                        # Only include observations from last 24 hours
                        if time_diff <= 24:
                            precip = observation['properties'].get('precipitationLastHour', {})
                            if precip and precip.get('value') is not None:
                                # Convert from mm to inches
                                precip_mm = precip['value']
                                precip_inches = precip_mm / 25.4
                                total_precipitation += precip_inches
                
                logger.info(f"24-hour precipitation: {total_precipitation:.2f} inches")
                return round(total_precipitation, 2)
            else:
                logger.warning("No observation stations found")
                return 0.0
                
        except Exception as e:
            logger.error(f"Error fetching precipitation data: {e}")
            return 0.0
    
    def scrape_school_closings(self):
        """
        Scrape school closings from CBS Boston website.
        Returns list of dictionaries with school closing information.
        """
        try:
            logger.info(f"Fetching school closings from: {self.school_closings_url}")
            response = requests.get(self.school_closings_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            school_data = []
            
            # Look for school closing entries
            # The structure may vary, so we'll try multiple patterns
            
            # Pattern 1: Look for list items or divs containing school information
            school_entries = soup.find_all(['li', 'div', 'tr'], class_=lambda x: x and any(
                keyword in x.lower() for keyword in ['school', 'closing', 'delay', 'district']
            ))
            
            if not school_entries:
                # Pattern 2: Look for tables with school data
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            school_entries.append(row)
            
            if not school_entries:
                # Pattern 3: Generic search for common patterns
                school_entries = soup.find_all(text=lambda t: t and any(
                    keyword in t.lower() for keyword in ['school', 'district', 'academy', 'elementary', 'high school']
                ))
            
            logger.info(f"Found {len(school_entries)} potential school entries")
            
            # Parse the entries
            for entry in school_entries:
                try:
                    text = entry.get_text(strip=True) if hasattr(entry, 'get_text') else str(entry).strip()
                    
                    # Skip if text is too short or doesn't contain relevant information
                    if len(text) < 5:
                        continue
                    
                    # Determine school type
                    school_type = 'Unknown'
                    if any(keyword in text.lower() for keyword in ['elementary', 'elem']):
                        school_type = 'Elementary'
                    elif any(keyword in text.lower() for keyword in ['middle', 'junior high']):
                        school_type = 'Middle'
                    elif any(keyword in text.lower() for keyword in ['high school', 'high']):
                        school_type = 'High'
                    elif 'district' in text.lower():
                        school_type = 'District'
                    elif any(keyword in text.lower() for keyword in ['college', 'university']):
                        school_type = 'College/University'
                    elif 'preschool' in text.lower() or 'pre-school' in text.lower():
                        school_type = 'Preschool'
                    
                    # Determine status
                    status = 'Unknown'
                    if any(keyword in text.lower() for keyword in ['closed', 'closing', 'no school']):
                        status = 'Closed'
                    elif any(keyword in text.lower() for keyword in ['delay', 'delayed']):
                        # Try to extract delay time
                        if '2 hour' in text.lower() or '2-hour' in text.lower():
                            status = '2-Hour Delay'
                        elif '3 hour' in text.lower() or '3-hour' in text.lower():
                            status = '3-Hour Delay'
                        else:
                            status = 'Delayed'
                    elif 'early release' in text.lower() or 'early dismissal' in text.lower():
                        status = 'Early Release'
                    elif 'cancelled' in text.lower() or 'canceled' in text.lower():
                        status = 'Cancelled'
                    
                    # Extract school name (first part of text, typically)
                    school_name = text.split('-')[0].split(':')[0].strip()
                    if len(school_name) > 100:
                        school_name = school_name[:100]
                    
                    # Only add if we have a valid status
                    if status != 'Unknown' and school_name:
                        school_data.append({
                            'school_name': school_name,
                            'school_type': school_type,
                            'status': status,
                            'raw_text': text[:200]  # Keep first 200 chars for reference
                        })
                
                except Exception as e:
                    logger.debug(f"Error parsing entry: {e}")
                    continue
            
            # Remove duplicates
            unique_schools = []
            seen = set()
            for school in school_data:
                key = (school['school_name'], school['status'])
                if key not in seen:
                    seen.add(key)
                    unique_schools.append(school)
            
            logger.info(f"Parsed {len(unique_schools)} unique school closings/delays")
            return unique_schools
            
        except requests.RequestException as e:
            logger.error(f"Error fetching school closings page: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error scraping school closings: {e}")
            return []
    
    def log_to_csv(self, school_data, precipitation):
        """
        Log school closings data to CSV file.
        
        Args:
            school_data: List of dictionaries with school information
            precipitation: Precipitation amount in inches
        """
        retrieval_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Check if file exists to determine if we need to write headers
        file_exists = os.path.isfile(self.output_file)
        
        try:
            with open(self.output_file, 'a', newline='', encoding='utf-8') as csvfile:
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
                
                # Write header if file is new
                if not file_exists:
                    writer.writeheader()
                
                # Write each school's data
                for school in school_data:
                    writer.writerow({
                        'retrieval_date': retrieval_time.split()[0],
                        'retrieval_time': retrieval_time.split()[1],
                        'school_name': school['school_name'],
                        'school_type': school['school_type'],
                        'status': school['status'],
                        'precipitation_24h_inches': precipitation,
                        'raw_text': school.get('raw_text', '')
                    })
            
            logger.info(f"Successfully logged {len(school_data)} entries to {self.output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing to CSV file: {e}")
            return False
    
    def run(self):
        """Main execution method."""
        logger.info("=" * 60)
        logger.info("School Closings Tracker - Starting")
        logger.info("=" * 60)
        
        # Fetch precipitation data
        logger.info("\n[1/3] Fetching 24-hour precipitation data...")
        precipitation = self.fetch_precipitation_data()
        
        # Scrape school closings
        logger.info("\n[2/3] Scraping school closings data...")
        school_data = self.scrape_school_closings()
        
        if not school_data:
            logger.warning("No school closings found. This could mean:")
            logger.warning("  - There are no closings today")
            logger.warning("  - The website structure has changed")
            logger.warning("  - There was an error accessing the website")
            
            # Log an empty entry to track the attempt
            school_data = [{
                'school_name': 'NO_CLOSINGS_FOUND',
                'school_type': 'N/A',
                'status': 'N/A',
                'raw_text': 'No school closings or delays found during this retrieval'
            }]
        
        # Log to CSV
        logger.info("\n[3/3] Logging data to CSV...")
        success = self.log_to_csv(school_data, precipitation)
        
        if success:
            logger.info("\n" + "=" * 60)
            logger.info("School Closings Tracker - Completed Successfully")
            logger.info(f"Total schools logged: {len(school_data)}")
            logger.info(f"24-hour precipitation: {precipitation} inches")
            logger.info(f"Output file: {self.output_file}")
            logger.info("=" * 60)
        else:
            logger.error("\n" + "=" * 60)
            logger.error("School Closings Tracker - Completed with Errors")
            logger.error("=" * 60)


def main():
    """Main entry point."""
    scraper = SchoolClosingsScraper()
    scraper.run()


if __name__ == '__main__':
    main()
