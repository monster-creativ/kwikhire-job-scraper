#!/usr/bin/env python3
import argparse
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('scraper.log')
    ]
)
logger = logging.getLogger(__name__)

class JobScraper:
    def __init__(self, job_board: str, location: str, keywords: Optional[str] = None):
        self.job_board = job_board.lower()
        self.location = location
        self.keywords = keywords
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })

    def get_indeed_url(self, page: int = 1) -> str:
        base_url = "https://za.indeed.com/jobs"
        params = {
            'q': self.keywords if self.keywords else '',
            'l': self.location,
            'start': (page - 1) * 10
        }
        return f"{base_url}?{'&'.join(f'{k}={v}' for k, v in params.items() if v)}"

    def get_careers24_url(self, page: int = 1) -> str:
        base_url = "https://www.careers24.com/jobs"
        params = {
            'keywords': self.keywords if self.keywords else '',
            'location': self.location,
            'page': page
        }
        return f"{base_url}?{'&'.join(f'{k}={v}' for k, v in params.items() if v)}"

    def get_pnet_url(self, page: int = 1) -> str:
        base_url = "https://www.pnet.co.za/jobs"
        params = {
            'keywords': self.keywords if self.keywords else '',
            'location': self.location,
            'page': page
        }
        return f"{base_url}?{'&'.join(f'{k}={v}' for k, v in params.items() if v)}"

    def scrape_indeed(self, max_pages: int = 1) -> List[Dict]:
        jobs = []
        for page in range(1, max_pages + 1):
            try:
                url = self.get_indeed_url(page)
                logger.info(f"Scraping Indeed page {page}: {url}")
                
                response = self.session.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                job_cards = soup.find_all('div', class_='job_seen_beacon')
                
                for card in job_cards:
                    try:
                        title_elem = card.find('h2', class_='jobTitle')
                        company_elem = card.find('span', class_='companyName')
                        location_elem = card.find('div', class_='companyLocation')
                        salary_elem = card.find('div', class_='salary-snippet')
                        description_elem = card.find('div', class_='job-snippet')
                        
                        job = {
                            'title': title_elem.text.strip() if title_elem else 'N/A',
                            'company': company_elem.text.strip() if company_elem else 'N/A',
                            'location': location_elem.text.strip() if location_elem else 'N/A',
                            'salary': salary_elem.text.strip() if salary_elem else 'N/A',
                            'description': description_elem.text.strip() if description_elem else 'N/A',
                            'url': 'https://za.indeed.com' + title_elem.find('a')['href'] if title_elem and title_elem.find('a') else 'N/A',
                            'posted_date': 'N/A',  # Indeed doesn't always show this
                            'requirements': 'N/A',  # Would need to visit job page
                            'job_board': 'Indeed',
                            'keywords': self.keywords if self.keywords else 'N/A'
                        }
                        jobs.append(job)
                        
                    except Exception as e:
                        logger.error(f"Error parsing Indeed job card: {e}")
                        continue
                
            except Exception as e:
                logger.error(f"Error scraping Indeed page {page}: {e}")
                continue
                
        return jobs

    def scrape_careers24(self, max_pages: int = 1) -> List[Dict]:
        jobs = []
        for page in range(1, max_pages + 1):
            try:
                url = self.get_careers24_url(page)
                logger.info(f"Scraping Careers24 page {page}: {url}")
                
                response = self.session.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                job_cards = soup.find_all('div', class_='job-card')
                
                for card in job_cards:
                    try:
                        title_elem = card.find('h3', class_='job-title')
                        company_elem = card.find('div', class_='company-name')
                        location_elem = card.find('div', class_='location')
                        salary_elem = card.find('div', class_='salary')
                        description_elem = card.find('div', class_='description')
                        date_elem = card.find('div', class_='date-posted')
                        
                        job = {
                            'title': title_elem.text.strip() if title_elem else 'N/A',
                            'company': company_elem.text.strip() if company_elem else 'N/A',
                            'location': location_elem.text.strip() if location_elem else 'N/A',
                            'salary': salary_elem.text.strip() if salary_elem else 'N/A',
                            'description': description_elem.text.strip() if description_elem else 'N/A',
                            'url': 'https://www.careers24.com' + title_elem.find('a')['href'] if title_elem and title_elem.find('a') else 'N/A',
                            'posted_date': date_elem.text.strip() if date_elem else 'N/A',
                            'requirements': 'N/A',  # Would need to visit job page
                            'job_board': 'Careers24',
                            'keywords': self.keywords if self.keywords else 'N/A'
                        }
                        jobs.append(job)
                        
                    except Exception as e:
                        logger.error(f"Error parsing Careers24 job card: {e}")
                        continue
                
            except Exception as e:
                logger.error(f"Error scraping Careers24 page {page}: {e}")
                continue
                
        return jobs

    def scrape_pnet(self, max_pages: int = 1) -> List[Dict]:
        jobs = []
        for page in range(1, max_pages + 1):
            try:
                url = self.get_pnet_url(page)
                logger.info(f"Scraping PNet page {page}: {url}")
                
                response = self.session.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                job_cards = soup.find_all('div', class_='job-item')
                
                for card in job_cards:
                    try:
                        title_elem = card.find('h3', class_='job-title')
                        company_elem = card.find('div', class_='company-name')
                        location_elem = card.find('div', class_='location')
                        salary_elem = card.find('div', class_='salary')
                        description_elem = card.find('div', class_='description')
                        date_elem = card.find('div', class_='date-posted')
                        
                        job = {
                            'title': title_elem.text.strip() if title_elem else 'N/A',
                            'company': company_elem.text.strip() if company_elem else 'N/A',
                            'location': location_elem.text.strip() if location_elem else 'N/A',
                            'salary': salary_elem.text.strip() if salary_elem else 'N/A',
                            'description': description_elem.text.strip() if description_elem else 'N/A',
                            'url': 'https://www.pnet.co.za' + title_elem.find('a')['href'] if title_elem and title_elem.find('a') else 'N/A',
                            'posted_date': date_elem.text.strip() if date_elem else 'N/A',
                            'requirements': 'N/A',  # Would need to visit job page
                            'job_board': 'PNet',
                            'keywords': self.keywords if self.keywords else 'N/A'
                        }
                        jobs.append(job)
                        
                    except Exception as e:
                        logger.error(f"Error parsing PNet job card: {e}")
                        continue
                
            except Exception as e:
                logger.error(f"Error scraping PNet page {page}: {e}")
                continue
                
        return jobs

    def scrape(self, max_pages: int = 1) -> List[Dict]:
        if self.job_board == 'indeed':
            return self.scrape_indeed(max_pages)
        elif self.job_board == 'careers24':
            return self.scrape_careers24(max_pages)
        elif self.job_board == 'pnet':
            return self.scrape_pnet(max_pages)
        else:
            raise ValueError(f"Unsupported job board: {self.job_board}")

def save_to_json(jobs: List[Dict], output_path: str) -> None:
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)

def save_to_csv(jobs: List[Dict], output_path: str) -> None:
    if not jobs:
        return
        
    headers = jobs[0].keys()
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(jobs)

def main():
    parser = argparse.ArgumentParser(description='Job Scraper')
    parser.add_argument('--job-board', required=True, help='Job board to scrape (indeed, careers24, pnet)')
    parser.add_argument('--location', required=True, help='Location to search in')
    parser.add_argument('--keywords', help='Keywords to search for')
    parser.add_argument('--max-pages', type=int, default=1, help='Maximum number of pages to scrape')
    parser.add_argument('--output-dir', required=True, help='Directory to save results')
    parser.add_argument('--csv-filename', required=True, help='CSV output filename')
    parser.add_argument('--json-filename', required=True, help='JSON output filename')
    
    args = parser.parse_args()
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Initialize scraper
        scraper = JobScraper(
            job_board=args.job_board,
            location=args.location,
            keywords=args.keywords
        )
        
        # Scrape jobs
        logger.info(f"Starting scraping for {args.job_board} in {args.location}")
        jobs = scraper.scrape(max_pages=args.max_pages)
        logger.info(f"Found {len(jobs)} jobs")
        
        # Save results
        json_path = os.path.join(args.output_dir, args.json_filename)
        csv_path = os.path.join(args.output_dir, args.csv_filename)
        
        save_to_json(jobs, json_path)
        save_to_csv(jobs, csv_path)
        
        logger.info(f"Results saved to:\nJSON: {json_path}\nCSV: {csv_path}")
        
        # Print JSON for PHP to capture
        print(json.dumps(jobs))
        
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 