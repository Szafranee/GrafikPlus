import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional
import logging
from dotenv import load_dotenv

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
    username: str = '***REMOVED***'
    password: str = '***REMOVED***'
    login_url: str = 'https://gpt.canalplus.pl/Account/Login?ReturnUrl=%2f'
    schedule_url: str = 'https://gpt.canalplus.pl/User/Schedule/'
    output_file: str = 'CanalPlus_schedule.csv'
    temp_file: str = 'temp_input.csv'
    parser: str = 'html.parser'
    encoding: str = 'utf-8'
    request_timeout: int = 30

    @classmethod
    def from_env(cls) -> 'ScraperConfig':
        """Creates configuration from environment variables"""
        load_dotenv()
        return cls(
            username=os.getenv('SCRAPER_USERNAME', cls.username),
            password=os.getenv('SCRAPER_PASSWORD', cls.password),
            login_url=os.getenv('SCRAPER_LOGIN_URL', cls.login_url),
            schedule_url=os.getenv('SCRAPER_SCHEDULE_URL', cls.schedule_url),
            output_file=os.getenv('SCRAPER_OUTPUT_FILE', cls.output_file),
            temp_file=os.getenv('SCRAPER_TEMP_FILE', cls.temp_file)
        )

class ScheduleScraper:
    def __init__(self, config: ScraperConfig):
        self.config = config
        self.session = requests.Session()
        self.schedule_data = []

    def login(self) -> bool:
        """Perform login to the system"""
        try:
            payload = {
                'username': self.config.username,
                'password': self.config.password
            }
            response = self.session.post(
                self.config.login_url,
                data=payload,
                timeout=self.config.request_timeout
            )
            response.raise_for_status()
            logging.info("Login successful")
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Login error: {e}")
            return False

    def fetch_schedule(self) -> Optional[str]:
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

class ScheduleParser:
    def __init__(self, html_content: str):
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.schedule_data = []

    @staticmethod
    def _calculate_duration(start_time: str, end_time: str) -> str:
        """Calculate duration between two times, handling day changes"""
        start = datetime.strptime(start_time, '%H:%M')
        end = datetime.strptime(end_time, '%H:%M')

        if end < start:
            end += timedelta(days=1)

        duration = end - start
        hours = duration.total_seconds() / 3600
        return f"{hours:.2f}"

    def parse_schedule(self) -> List[Dict]:
        """Parse schedule data from HTML content"""
        sections = self.soup.find_all('th', class_='gpt-table-section-header')

        for section in sections:
            date = section.text.strip()

            current_section = section.parent
            rows = current_section.find_next_siblings('tr')

            for row in rows:
                cells = row.find_all('td')
                if not cells:
                    continue

                program_cell = row.find('span')
                if not program_cell:
                    continue

                try:
                    program = program_cell.text.strip()
                    location = cells[3].find('span').text.strip()

                    time_cell = cells[4].find('span', class_='text-bold')
                    if not time_cell:
                        continue

                    times = time_cell.text.strip().replace('\xa0', ' ').split(' - ')
                    if len(times) != 2:
                        continue

                    start_time, end_time = times
                    duration = self._calculate_duration(start_time, end_time)

                    remarks_cell = row.find('pre', class_='gpt-pre-remarks')
                    remarks = remarks_cell.text.strip() if remarks_cell else ""

                    self.schedule_data.append({
                        'date': date,
                        'program': program,
                        'location': location,
                        'start_time': start_time,
                        'end_time': end_time,
                        'duration': duration,
                        'remarks': remarks
                    })
                except (AttributeError, IndexError) as e:
                    logging.warning(f"Error parsing row: {e}")
                    continue

        return self.schedule_data

    def save_to_csv(self, filename: str) -> None:
        """Save parsed schedule to CSV file"""
        headers = ['Data', 'Program', 'Miejsce produkcji', 'Od', 'Do', 'Godziny', 'Uwagi']

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(headers)

            for entry in self.schedule_data:
                writer.writerow([
                    entry['date'],
                    entry['program'],
                    entry['location'],
                    entry['start_time'],
                    entry['end_time'],
                    entry['duration'],
                    entry['remarks']
                ])

def main():
    """Main execution function"""
    config = ScraperConfig.from_env()

    scraper = ScheduleScraper(config)
    if not scraper.login():
        logging.error("Login failed. Terminating program.")
        return

    html_content = scraper.fetch_schedule()
    if not html_content:
        logging.error("Failed to fetch schedule. Terminating program.")
        return

    parser = ScheduleParser(html_content)
    parser.parse_schedule()
    parser.save_to_csv(config.output_file)
    logging.info(f"Schedule saved to {config.output_file}")

if __name__ == "__main__":
    main()