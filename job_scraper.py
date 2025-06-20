import os
import time
import json
from datetime import datetime
from scrapers.careers24_scraper import Careers24Scraper
from config import JOB_BOARDS, OUTPUT_DIR, CSV_FILENAME, JSON_FILENAME

class JobScraperManager:
    def __init__(self):
        self.scrapers = {
            'careers24': Careers24Scraper(),
            # Add more scrapers as they are implemented
        }
        self.all_jobs = []
        
    def scrape_all_jobs(self):
        """Scrape jobs from all configured job boards"""
        for board_name, url in JOB_BOARDS.items():
            if board_name in self.scrapers:
                print(f"Scraping {board_name}...")
                scraper = self.scrapers[board_name]
                scraper.scrape_jobs(url)
                self.all_jobs.extend(scraper.jobs)
                print(f"Found {len(scraper.jobs)} jobs on {board_name}")
    
    def save_results(self):
        """Save all scraped jobs to CSV and JSON"""
        if not self.all_jobs:
            print("No jobs found to save")
            return
            
        # Create output directory if it doesn't exist
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Save to CSV
        csv_path = os.path.join(OUTPUT_DIR, CSV_FILENAME)
        with open(csv_path, 'w', encoding='utf-8') as f:
            # Write header
            f.write(','.join(self.all_jobs[0].keys()) + '\n')
            # Write data
            for job in self.all_jobs:
                f.write(','.join(str(job.get(key, '')) for key in job.keys()) + '\n')
        print(f"Saved {len(self.all_jobs)} jobs to {csv_path}")
        
        # Save to JSON
        json_path = os.path.join(OUTPUT_DIR, JSON_FILENAME)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.all_jobs, f, indent=4, ensure_ascii=False)
        print(f"Saved {len(self.all_jobs)} jobs to {json_path}")

if __name__ == "__main__":
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Initialize and run scraper
    manager = JobScraperManager()
    manager.scrape_all_jobs()
    manager.save_results() 