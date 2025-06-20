# Job Board URLs
JOB_BOARDS = {
    'careers24': 'https://www.careers24.com/jobs/',
    'pnet': 'https://www.pnet.co.za/jobs/',
    'indeed': 'https://za.indeed.com/',
    'careerjunction': 'https://www.careerjunction.co.za/',
    'jobmail': 'https://www.jobmail.co.za/'
}

# Search parameters
SEARCH_PARAMS = {
    'location': 'South Africa',
    'radius': '50',  # km
    'sort_by': 'date'  # date, relevance, salary
}

# Output settings
OUTPUT_DIR = 'output'
CSV_FILENAME = 'sa_jobs.csv'
JSON_FILENAME = 'sa_jobs.json'

# Scraping settings
REQUEST_DELAY = 3  # seconds between requests
MAX_RETRIES = 3
TIMEOUT = 30  # seconds

# Job fields to scrape
JOB_FIELDS = [
    'job_title',
    'job_description',
    'role_description',
    'qualifications_skills',
    'job_location',
    'salary',
    'job_type',
    'experience_level',
    'closing_date'
] 