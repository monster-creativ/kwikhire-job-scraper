from scrapers.careers24_scraper import Careers24Scraper
import json
import os
from datetime import datetime

def test_scraper():
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    os.makedirs('output/logos', exist_ok=True)
    
    # Initialize the scraper
    print("Initializing Careers24 scraper...")
    scraper = Careers24Scraper()
    
    # Test URL - using Careers24's job search page
    test_url = "https://www.careers24.com/jobs/"
    
    print(f"Starting to scrape jobs from {test_url}")
    print("This may take a few minutes...")
    
    # Run the scraper
    scraper.scrape_jobs(test_url)
    
    # Print results
    print("\nScraping completed!")
    print(f"Found {len(scraper.jobs)} jobs")
    
    # Save results to JSON for inspection
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"output/test_results_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(scraper.jobs, f, indent=4, ensure_ascii=False)
    
    print(f"\nResults saved to: {output_file}")
    
    # Print sample of first job (if any found)
    if scraper.jobs:
        print("\nSample of first job found:")
        first_job = scraper.jobs[0]
        for key, value in first_job.items():
            print(f"{key}: {value[:100] if isinstance(value, str) else value}...")

if __name__ == "__main__":
    test_scraper() 