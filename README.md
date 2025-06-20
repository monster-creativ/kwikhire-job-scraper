# South African Job Scraper

A web scraping tool designed to collect job listings from various South African job boards.

## Features

- Scrapes multiple South African job boards
- Extracts key job information:
  - Job Title
  - Job Description
  - Role Description
  - Qualifications/Skills
  - Job Location
  - Salary
  - Job Type
  - Experience Level
  - Closing Date
- Saves data in both CSV and JSON formats
- Handles rate limiting and anti-bot measures
- Uses rotating user agents

## Setup

1. Install Python 3.8 or higher
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Chrome browser (required for Selenium)

## Usage

1. Configure job boards and settings in `config.py`
2. Run the scraper:
   ```bash
   python job_scraper.py
   ```

## Output

The scraper generates two files:
- `sa_jobs.csv`: CSV format of all scraped jobs
- `sa_jobs.json`: JSON format of all scraped jobs

## Supported Job Boards

- Careers24
- PNet
- Indeed South Africa
- CareerJunction
- JobMail

## Notes

- Respect robots.txt and rate limiting
- Add appropriate delays between requests
- Some job boards may require authentication
- Web scraping may be against some websites' terms of service

## License

MIT License 