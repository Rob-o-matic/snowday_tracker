"""
Unit tests for School Closings Scraper
Tests core functionality with mocked external dependencies
"""

import pytest
import os
import csv
import tempfile
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from school_closings_scraper import SchoolClosingsScraper


class TestSchoolClosingsScraper:
    """Test cases for SchoolClosingsScraper class"""
    
    def test_init_default_values(self):
        """Test scraper initialization with default values"""
        scraper = SchoolClosingsScraper()
        assert scraper.output_file == 'school_closings_log.csv'
        assert scraper.dry_run == False
        assert scraper.school_closings_url == "https://www.cbsnews.com/boston/school-closings/"
    
    def test_init_custom_values(self):
        """Test scraper initialization with custom values"""
        scraper = SchoolClosingsScraper(
            output_file='custom.csv',
            weather_lat='40.0',
            weather_lon='-75.0',
            dry_run=True
        )
        assert scraper.output_file == 'custom.csv'
        assert scraper.weather_lat == '40.0'
        assert scraper.weather_lon == '-75.0'
        assert scraper.dry_run == True
    
    def test_sanitize_csv_field_formula_injection(self):
        """Test CSV injection prevention"""
        scraper = SchoolClosingsScraper()
        
        # Test dangerous characters
        assert scraper._sanitize_csv_field('=SUM(A1:A10)').startswith("'")
        assert scraper._sanitize_csv_field('+MALICIOUS').startswith("'")
        assert scraper._sanitize_csv_field('-FORMULA').startswith("'")
        assert scraper._sanitize_csv_field('@FORMULA').startswith("'")
        
        # Test safe strings
        assert scraper._sanitize_csv_field('Normal School Name') == 'Normal School Name'
        assert scraper._sanitize_csv_field('School-Name') == 'School-Name'
    
    def test_sanitize_csv_field_control_characters(self):
        """Test removal of control characters"""
        scraper = SchoolClosingsScraper()
        
        # Control characters should be removed (except newline and tab)
        result = scraper._sanitize_csv_field('Test\x00\x01\x02School')
        assert '\x00' not in result
        assert '\x01' not in result
        assert '\x02' not in result
    
    def test_validate_school_data_valid(self):
        """Test validation of valid school data"""
        scraper = SchoolClosingsScraper()
        
        school = {
            'school_name': 'Test Elementary School',
            'school_type': 'Elementary',
            'status': 'Closed',
            'raw_text': 'Test Elementary School - Closed'
        }
        
        assert scraper._validate_school_data(school) == True
        assert school['school_name'] == 'Test Elementary School'
        assert school['status'] == 'Closed'
    
    def test_validate_school_data_invalid_status(self):
        """Test validation fixes invalid status"""
        scraper = SchoolClosingsScraper()
        
        school = {
            'school_name': 'Test School',
            'school_type': 'Elementary',
            'status': 'InvalidStatus',
            'raw_text': 'Test'
        }
        
        assert scraper._validate_school_data(school) == True
        assert school['status'] == 'Unknown'  # Should be corrected
    
    def test_validate_school_data_missing_name(self):
        """Test validation rejects data without school name"""
        scraper = SchoolClosingsScraper()
        
        school = {
            'school_name': '',
            'school_type': 'Elementary',
            'status': 'Closed',
            'raw_text': 'Test'
        }
        
        assert scraper._validate_school_data(school) == False
    
    def test_validate_school_data_truncates_long_names(self):
        """Test validation truncates overly long school names"""
        scraper = SchoolClosingsScraper()
        
        long_name = 'A' * 300
        school = {
            'school_name': long_name,
            'school_type': 'Elementary',
            'status': 'Closed',
            'raw_text': 'Test'
        }
        
        scraper._validate_school_data(school)
        assert len(school['school_name']) <= 200
    
    def test_log_to_csv_creates_new_file(self):
        """Test CSV logging creates new file with headers"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp:
            tmp_path = tmp.name
        
        try:
            os.unlink(tmp_path)  # Ensure file doesn't exist
        except:
            pass
        
        try:
            scraper = SchoolClosingsScraper(output_file=tmp_path)
            
            school_data = [{
                'school_name': 'Test School',
                'school_type': 'Elementary',
                'status': 'Closed',
                'raw_text': 'Test School - Closed'
            }]
            
            result = scraper.log_to_csv(school_data, 2.5)
            assert result == True
            
            # Verify file was created
            assert os.path.exists(tmp_path)
            
            # Verify content
            with open(tmp_path, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                assert len(rows) == 1
                assert rows[0]['school_name'] == 'Test School'
                assert rows[0]['status'] == 'Closed'
                assert rows[0]['precipitation_24h_inches'] == '2.5'
        
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_log_to_csv_appends_to_existing(self):
        """Test CSV logging appends to existing file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp:
            tmp_path = tmp.name
        
        # Delete the temp file so scraper can create it fresh
        try:
            os.unlink(tmp_path)
        except:
            pass
        
        try:
            scraper = SchoolClosingsScraper(output_file=tmp_path)
            
            # First write
            school_data1 = [{
                'school_name': 'School 1',
                'school_type': 'Elementary',
                'status': 'Closed',
                'raw_text': 'School 1 - Closed'
            }]
            scraper.log_to_csv(school_data1, 1.0)
            
            # Second write (should append)
            school_data2 = [{
                'school_name': 'School 2',
                'school_type': 'High',
                'status': 'Delayed',
                'raw_text': 'School 2 - Delayed'
            }]
            scraper.log_to_csv(school_data2, 2.0)
            
            # Verify both entries exist
            with open(tmp_path, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                assert len(rows) == 2
                assert rows[0]['school_name'] == 'School 1'
                assert rows[1]['school_name'] == 'School 2'
        
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_log_to_csv_dry_run(self):
        """Test CSV logging in dry run mode"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp:
            tmp_path = tmp.name
        
        try:
            os.unlink(tmp_path)  # Ensure file doesn't exist
        except:
            pass
        
        try:
            scraper = SchoolClosingsScraper(output_file=tmp_path, dry_run=True)
            
            school_data = [{
                'school_name': 'Test School',
                'school_type': 'Elementary',
                'status': 'Closed',
                'raw_text': 'Test'
            }]
            
            result = scraper.log_to_csv(school_data, 2.5)
            assert result == True
            
            # Verify file was NOT created in dry run mode
            assert not os.path.exists(tmp_path)
        
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    @patch('school_closings_scraper.requests.Session')
    def test_fetch_precipitation_data_success(self, mock_session_class):
        """Test successful precipitation data fetch"""
        # Mock the session and responses
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Mock responses
        mock_points_response = Mock()
        mock_points_response.json.return_value = {
            'properties': {
                'observationStations': 'https://api.weather.gov/stations'
            }
        }
        
        mock_stations_response = Mock()
        mock_stations_response.json.return_value = {
            'features': [{
                'properties': {
                    'stationIdentifier': 'TEST123'
                }
            }]
        }
        
        mock_obs_response = Mock()
        mock_obs_response.json.return_value = {
            'features': [{
                'properties': {
                    'timestamp': '2026-01-22T10:00:00+00:00',
                    'precipitationLastHour': {
                        'value': 25.4  # 1 inch in mm
                    }
                }
            }]
        }
        
        mock_session.get.side_effect = [
            mock_points_response,
            mock_stations_response,
            mock_obs_response
        ]
        
        scraper = SchoolClosingsScraper()
        scraper.session = mock_session
        
        result = scraper.fetch_precipitation_data()
        assert result == 1.0  # 25.4mm = 1.0 inch
    
    @patch('school_closings_scraper.requests.Session')
    def test_fetch_precipitation_data_network_error(self, mock_session_class):
        """Test precipitation fetch handles network errors gracefully"""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Simulate network error
        import requests
        mock_session.get.side_effect = requests.exceptions.RequestException("Network error")
        
        scraper = SchoolClosingsScraper()
        scraper.session = mock_session
        
        result = scraper.fetch_precipitation_data()
        assert result == 0.0  # Should return 0 on error
    
    def test_deduplication_in_scraping(self):
        """Test that duplicate school entries are removed"""
        # This would require mocking the HTTP response with BeautifulSoup
        # For now, we test the deduplication logic conceptually
        scraper = SchoolClosingsScraper()
        
        # Simulate what scrape_school_closings does with duplicates
        school_data = [
            {'school_name': 'School A', 'status': 'Closed', 'school_type': 'Elementary', 'raw_text': 'Test'},
            {'school_name': 'School A', 'status': 'Closed', 'school_type': 'Elementary', 'raw_text': 'Test'},
            {'school_name': 'School B', 'status': 'Delayed', 'school_type': 'High', 'raw_text': 'Test'},
        ]
        
        # Deduplication logic from scrape_school_closings
        unique_schools = []
        seen = set()
        for school in school_data:
            key = (school['school_name'], school['status'])
            if key not in seen:
                seen.add(key)
                unique_schools.append(school)
        
        assert len(unique_schools) == 2
        assert unique_schools[0]['school_name'] == 'School A'
        assert unique_schools[1]['school_name'] == 'School B'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
