# Snow Day Tracker

A tool for tracking school closings and delays from CBS Boston's school closings website, along with precipitation data from the National Weather Service.

## Features

- Scrapes school closing and delay information from [CBS Boston School Closings](https://www.cbsnews.com/boston/school-closings/)
- Logs the following information for each school:
  - School name
  - School type (Elementary, Middle, High, District, etc.)
  - Status (Closed, Delayed, Early Release, Cancelled)
  - Date and time of retrieval
- Retrieves 24-hour precipitation data from weather.gov API
- Stores all data in a CSV file for easy analysis

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

3. (Optional) Configure location for weather data:
```bash
cp .env.example .env
# Edit .env to set your preferred coordinates (defaults to Boston area)
```

## Usage

Run the scraper:
```bash
python school_closings_scraper.py
```

The script will:
1. Fetch 24-hour precipitation data for the Boston area
2. Scrape school closing information from CBS Boston
3. Log all data to `school_closings_log.csv`

## Output Format

The CSV file contains the following columns:
- `retrieval_date` - Date when the data was retrieved
- `retrieval_time` - Time when the data was retrieved
- `school_name` - Name of the school or district
- `school_type` - Type of school (Elementary, Middle, High, District, etc.)
- `status` - Closing/delay status (Closed, 2-Hour Delay, Early Release, etc.)
- `precipitation_24h_inches` - Total precipitation in last 24 hours (inches)
- `raw_text` - Raw text from the source (for reference)

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