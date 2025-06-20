from .base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time
import logging

class Careers24Scraper(BaseScraper):
    def scrape_jobs(self, url):
        """Scrape jobs from Careers24"""
        try:
            logging.info(f"Starting to scrape Careers24: {url}")
            self.driver.get(url)
            time.sleep(3)  # Initial page load
            
            # Wait for job listings to load
            try:
                job_cards = self.wait_for_element(By.CLASS_NAME, "job-card")
                if not job_cards:
                    logging.warning("No job cards found on the page")
                    return
            except TimeoutException:
                logging.error("Timeout waiting for job cards to load")
                raise Exception("Page took too long to load. Please try again.")
            
            # Get all job cards
            try:
                job_cards = self.driver.find_elements(By.CLASS_NAME, "job-card")
                logging.info(f"Found {len(job_cards)} job cards")
            except NoSuchElementException:
                logging.error("Could not find job cards on the page")
                raise Exception("Could not find any job listings. The page structure might have changed.")
            
            for index, card in enumerate(job_cards, 1):
                try:
                    logging.info(f"Processing job card {index} of {len(job_cards)}")
                    
                    # Extract company details first
                    company_data = self.extract_company_details(card)
                    
                    # Download company logo if available
                    if company_data['company_logo']:
                        try:
                            company_data['company_logo'] = self.download_company_logo(
                                company_data['company_logo'],
                                company_data['company_name']
                            )
                        except Exception as e:
                            logging.warning(f"Failed to download logo for {company_data['company_name']}: {str(e)}")
                    
                    # Extract job data
                    try:
                        job_data = {
                            'job_title': self.extract_text(card.find_element(By.CLASS_NAME, "job-title")),
                            'job_location': self.extract_text(card.find_element(By.CLASS_NAME, "job-location")),
                            'job_type': self.extract_text(card.find_element(By.CLASS_NAME, "job-type")),
                            'salary': self.clean_salary(self.extract_text(card.find_element(By.CLASS_NAME, "salary"))),
                            'closing_date': self.parse_date(self.extract_text(card.find_element(By.CLASS_NAME, "closing-date")))
                        }
                    except NoSuchElementException as e:
                        logging.warning(f"Failed to extract basic job data: {str(e)}")
                        continue
                    
                    # Merge company data with job data
                    job_data.update(company_data)
                    
                    # Click on job card to get full details
                    try:
                        card.click()
                        time.sleep(2)
                    except WebDriverException as e:
                        logging.warning(f"Failed to click job card: {str(e)}")
                        continue
                    
                    # Get job description
                    try:
                        description_element = self.wait_for_element(By.CLASS_NAME, "job-description")
                        if description_element:
                            job_data['job_description'] = self.extract_text(description_element)
                    except TimeoutException:
                        logging.warning("Timeout waiting for job description")
                    
                    # Get role description
                    try:
                        role_element = self.wait_for_element(By.CLASS_NAME, "role-description")
                        if role_element:
                            job_data['role_description'] = self.extract_text(role_element)
                    except TimeoutException:
                        logging.warning("Timeout waiting for role description")
                    
                    # Get qualifications
                    try:
                        qualifications_element = self.wait_for_element(By.CLASS_NAME, "qualifications")
                        if qualifications_element:
                            job_data['qualifications_skills'] = self.extract_text(qualifications_element)
                    except TimeoutException:
                        logging.warning("Timeout waiting for qualifications")
                    
                    # Get experience level
                    try:
                        experience_element = self.wait_for_element(By.CLASS_NAME, "experience-level")
                        if experience_element:
                            job_data['experience_level'] = self.extract_text(experience_element)
                    except TimeoutException:
                        logging.warning("Timeout waiting for experience level")
                    
                    # Get additional company details from job page
                    try:
                        company_details_element = self.wait_for_element(By.CLASS_NAME, "company-details")
                        if company_details_element:
                            additional_company_data = self.extract_company_details(company_details_element)
                            # Update company data if we found more details
                            for key, value in additional_company_data.items():
                                if value and not job_data.get(key):
                                    job_data[key] = value
                    except TimeoutException:
                        logging.warning("Timeout waiting for company details")
                    
                    self.jobs.append(job_data)
                    logging.info(f"Successfully processed job: {job_data['job_title']}")
                    
                    # Go back to job listings
                    try:
                        self.driver.back()
                        time.sleep(1)
                    except WebDriverException as e:
                        logging.warning(f"Failed to go back to job listings: {str(e)}")
                        # Try to reload the page
                        self.driver.get(url)
                        time.sleep(3)
                    
                except Exception as e:
                    logging.error(f"Error processing job card {index}: {str(e)}")
                    continue
            
            logging.info(f"Successfully scraped {len(self.jobs)} jobs")
            
        except Exception as e:
            logging.error(f"Error scraping Careers24: {str(e)}")
            raise
        finally:
            self.close() 