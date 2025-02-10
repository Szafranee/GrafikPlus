import logging
from dataclasses import dataclass
from typing import Optional

import requests

from schedule_parser import ScheduleParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)


@dataclass
class ScraperConfig:
    """Configuration storage class for web scraping operations"""
    login_url: str = 'https://gpt.canalplus.pl/Account/Login'
    schedule_url: str = 'https://gpt.canalplus.pl/Schedule/Editing'
    parser: str = 'html.parser'
    encoding: str = 'utf-8'
    request_timeout: int = 30


class ScheduleScraper:
    def __init__(self, credentials):
        self.config = ScraperConfig()
        self.session = requests.Session()
        self.schedule_data = []
        self.credentials = credentials

    def __login(self) -> bool:
        """Perform login to the system"""
        try:
            payload = {
                'username': self.credentials["username"],
                'password': self.credentials["password"]
            }
            response = self.session.post(
                self.config.login_url,
                data=payload,
                timeout=self.config.request_timeout
            )
            response.raise_for_status()

            # Check for error message in response
            error_message = "Niepoprawny identyfikator lub hasło."
            if error_message in response.text:
                logging.error("Invalid credentials")
                return False

            logging.info("Login successful")
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Login error: {e}")
            return False

    def __fetch_schedule(self) -> Optional[str]:
        """Fetch schedule HTML content"""
        try:
            response = self.session.get(
                self.config.schedule_url,
                timeout=self.config.request_timeout
            )
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching schedule: {e}")
            return None

    def scrape_schedule(self) -> bool:
        """Main execution function"""

        if not self.__login():
            logging.error("Login failed. Terminating program.")
            return False

        html_content = self.__fetch_schedule()
        if not html_content:
            logging.error("Failed to fetch schedule. Terminating program.")
            return False

        parser = ScheduleParser(html_content, self.credentials)
        parser.parse_schedule()
        parser.save_to_csv()
        logging.info(f"Schedule saved to {self.credentials["output_filename"]}")
        return True
