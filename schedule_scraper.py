import logging
from typing import Optional

import requests

from config import ScheduleConfig, ScraperConfig
from schedule_parser import ScheduleParser

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

    @staticmethod
    def __convert_date_to_url_format(date: str) -> str:
        """Convert date to URL format from dates like '01/01/2025'"""
        day, month, year = date.split('.')
        return f"{month}%2F{day}%2F{year}%2000%3A00%3A00"

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

        date_url = self.__convert_date_to_url_format(self.schedule_config.selected_date)

        schedule_url += f"?date={date_url}"  # Add date to URL

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

        # Calls the appropriate parsing method based on the schedule type from the config
        parser.parse_schedule()

        parser.save_to_xlsx()
        logging.info(f"Schedule saved to {self.schedule_config.output_filename}")
        return True
