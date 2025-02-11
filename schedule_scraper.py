import logging
from typing import Optional

import requests

from schedule_parser import ScheduleParser
from config import ScheduleConfig, ScraperConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        # logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)


class ScheduleScraper:
    def __init__(self, schedule_config: ScheduleConfig):
        self.config = ScraperConfig()
        self.session = requests.Session()
        self.schedule_data = []
        self.schedule_config = schedule_config

    def __login(self) -> bool:
        """Perform login to the system"""
        try:
            payload = {
                'username': self.schedule_config.username,
                'password': self.schedule_config.password
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
        schedule_url = self.config.personal_schedule_url if self.schedule_config.is_personal else self.config.general_schedule_url

        try:
            response = self.session.get(
                schedule_url,
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

        parser = ScheduleParser(html_content, self.schedule_config)
        parser.parse_schedule()
        parser.save_to_csv()
        logging.info(f"Schedule saved to {self.schedule_config.output_filename}")
        return True
