# Snow Day Tracker

A robust tool for tracking school closings and delays from CBS Boston's school closings website, along with precipitation data from the National Weather Service.

## Features

- Scrapes school closing and delay information from [CBS Boston School Closings](https://www.cbsnews.com/boston/school-closings/)
- Logs the following information for each school:
  - School name
  - School type (Elementary, Middle, High, District, etc.)
  - Status (Closed, Delayed, Early Release, Cancelled)
  - Date and time of retrieval
- Retrieves 24-hour precipitation data from weather.gov API
- Stores all data in a CSV file for easy analysis
- **NEW**: Command-line interface with configurable options
- **NEW**: Automatic retry logic for network failures
- **NEW**: Input validation and CSV injection protection
- **NEW**: Comprehensive unit test suite

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Rob-o-matic/snowday_tracker.git
cd snowday_tracker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or use the Makefile:
```bash
make install
```

3. (Optional) Configure location for weather data:
```bash
cp .env.example .env
# Edit .env to set your preferred coordinates (defaults to Boston area)
```

## Usage

### Basic Usage

Run the scraper with default settings:
```bash
python school_closings_scraper.py
```

Or use the provided runner script:
```bash
./run_scraper.sh
```

Or use Make:
```bash
make run
```

### Advanced Usage

The scraper now supports command-line arguments for flexible configuration:

```bash
# Specify custom output file
python school_closings_scraper.py --output data/closings.csv

# Use custom coordinates
python school_closings_scraper.py --lat 42.3601 --lon -71.0589

# Dry run (test without writing)
python school_closings_scraper.py --dry-run

# Verbose logging
python school_closings_scraper.py --verbose

# Combine options
python school_closings_scraper.py -o data/today.csv --verbose --dry-run
```

View all options:
```bash
python school_closings_scraper.py --help
```

### Analyzing the Data

Use the included analysis script to get insights from collected data:
```bash
python analyze_data.py
```

This will show:
- Total number of closings/delays
- Breakdown by status (closed, delayed, etc.)
- Breakdown by school type
- Precipitation statistics
- Schools with most closings

### Testing

Run the comprehensive unit test suite:
```bash
make test
```

Or:
```bash
python -m pytest tests/ -v
```

Or use the test runner:
```bash
./run_tests.sh
```

Test with mock data (doesn't require network):
```bash
python test_scraper.py
```

## Output Format

The CSV file contains the following columns:
- `retrieval_date` - Date when the data was retrieved
- `retrieval_time` - Time when the data was retrieved
- `school_name` - Name of the school or district (sanitized for CSV injection)
- `school_type` - Type of school (Elementary, Middle, High, District, etc.)
- `status` - Closing/delay status (Closed, 2-Hour Delay, Early Release, etc.)
- `precipitation_24h_inches` - Total precipitation in last 24 hours (inches)
- `raw_text` - Raw text from the source (for reference)

## Improvements in v1.1.0

This version includes significant improvements based on QA feedback:

### Reliability
- ✅ **Automatic retry logic** - Network requests retry up to 3 times with exponential backoff
- ✅ **Better error handling** - Specific exception types with informative messages
- ✅ **Data validation** - Validates all scraped data before saving

### Security
- ✅ **CSV injection protection** - Sanitizes fields to prevent formula execution
- ✅ **Input validation** - Validates and truncates all fields appropriately

### Testing
- ✅ **14 comprehensive unit tests** - Testing all core functionality
- ✅ **Mocked external dependencies** - Tests run without network access
- ✅ **Easy test running** - `make test` or `./run_tests.sh`

### Usability
- ✅ **Command-line interface** - Configure everything via CLI arguments
- ✅ **Dry-run mode** - Test without writing files (`--dry-run`)
- ✅ **Verbose logging** - Debug mode available (`--verbose`)
- ✅ **Custom output paths** - Specify output location
- ✅ **Makefile** - Common tasks: `make install`, `make test`, `make run`

### Code Quality
- ✅ **Better logging** - Clear status indicators (✓/✗/⚠)
- ✅ **Exit codes** - Proper exit codes for automation
- ✅ **Documentation** - Comprehensive docstrings and examples

## Scheduling

To run the scraper automatically, you can set up a cron job (Linux/Mac) or Task Scheduler (Windows).

Example cron job to run daily at 6 AM:
```bash
0 6 * * * cd /path/to/snowday_tracker && python school_closings_scraper.py >> logs/scraper.log 2>&1
```

## API Usage

The tool uses the following APIs:
- **CBS Boston School Closings**: Public website (no API key required)
- **weather.gov API**: National Weather Service API (no API key required)

## Requirements

- Python 3.7+
- Internet connection
- Dependencies listed in requirements.txt

## License

MIT License

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.