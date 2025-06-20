from abc import ABC, abstractmethod
import time
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import requests
import os

class BaseScraper(ABC):
    def __init__(self):
        self.jobs = []
        self.setup_driver()
        
    def setup_driver(self):
        """Setup Selenium WebDriver with Chrome"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        ua = UserAgent()
        chrome_options.add_argument(f'user-agent={ua.random}')
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.wait = WebDriverWait(self.driver, 10)
    
    @abstractmethod
    def scrape_jobs(self, url):
        """Main method to scrape jobs from a given URL"""
        pass
    
    def extract_text(self, element):
        """Safely extract text from an element"""
        return element.get_text(strip=True) if element else ""
    
    def extract_company_details(self, element):
        """Extract company details from an element"""
        company_data = {
            'company_name': '',
            'company_logo': '',
            'company_phone': '',
            'company_email': '',
            'company_website': '',
            'company_address': ''
        }
        
        try:
            # Extract company name
            name_element = element.find_element(By.CLASS_NAME, "company-name")
            company_data['company_name'] = self.extract_text(name_element)
            
            # Extract company logo
            logo_element = element.find_element(By.CLASS_NAME, "company-logo")
            if logo_element:
                company_data['company_logo'] = logo_element.get_attribute('src')
            
            # Extract contact details
            contact_element = element.find_element(By.CLASS_NAME, "company-contact")
            if contact_element:
                # Phone
                phone_element = contact_element.find_element(By.CLASS_NAME, "company-phone")
                company_data['company_phone'] = self.extract_text(phone_element)
                
                # Email
                email_element = contact_element.find_element(By.CLASS_NAME, "company-email")
                company_data['company_email'] = self.extract_text(email_element)
                
                # Website
                website_element = contact_element.find_element(By.CLASS_NAME, "company-website")
                company_data['company_website'] = self.extract_text(website_element)
                
                # Address
                address_element = contact_element.find_element(By.CLASS_NAME, "company-address")
                company_data['company_address'] = self.extract_text(address_element)
        
        except Exception as e:
            print(f"Error extracting company details: {str(e)}")
        
        return company_data
    
    def download_company_logo(self, logo_url, company_name):
        """Download company logo and save it locally"""
        if not logo_url:
            return ""
            
        try:
            # Create logos directory if it doesn't exist
            os.makedirs('output/logos', exist_ok=True)
            
            # Generate filename from company name
            filename = f"output/logos/{company_name.lower().replace(' ', '_')}.png"
            
            # Download and save the image
            response = requests.get(logo_url)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                return filename
        except Exception as e:
            print(f"Error downloading logo: {str(e)}")
        
        return ""
    
    def parse_date(self, date_str):
        """Parse various date formats to standard format"""
        try:
            # Add more date formats as needed
            formats = [
                "%Y-%m-%d",
                "%d %B %Y",
                "%d/%m/%Y",
                "%d-%m-%Y",
                "%B %d, %Y"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
                except ValueError:
                    continue
            return date_str
        except:
            return date_str
    
    def clean_salary(self, salary_str):
        """Clean and standardize salary format"""
        if not salary_str:
            return ""
        # Remove currency symbols and standardize format
        salary_str = salary_str.replace("R", "").replace("ZAR", "").strip()
        return salary_str
    
    def wait_for_element(self, by, value, timeout=10):
        """Wait for an element to be present"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except:
            return None
    
    def close(self):
        """Close the browser"""
        if hasattr(self, 'driver'):
            self.driver.quit()
    
    def __del__(self):
        """Destructor to ensure browser is closed"""
        self.close() 