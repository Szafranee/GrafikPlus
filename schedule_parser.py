import csv
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

from bs4 import BeautifulSoup

from config import ScheduleConfig

class ScheduleParser:
    def __init__(self, html_content: str, schedule_config: ScheduleConfig):
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.schedule_data = []
        self.schedule_config = schedule_config

    @staticmethod
    def __calculate_duration(start_time: str, end_time: str) -> str:
        """Calculate duration between two times, handling day changes"""
        start = datetime.strptime(start_time, '%H:%M')
        end = datetime.strptime(end_time, '%H:%M')

        if end < start:
            end += timedelta(days=1)

        duration = end - start
        hours = duration.total_seconds() / 3600
        return f"{hours:.2f}"

    @staticmethod
    def __convert_date(date: str) -> str:
        """Convert date to ISO format from dates like 'poniedziałek, 1 stycznia 2025'"""

        date_parts = date.split(', ')

        date_string = date_parts[1]
        day, month, year = date_string.split(' ')

        months = {
            'stycznia': '01',
            'lutego': '02',
            'marca': '03',
            'kwietnia': '04',
            'maja': '05',
            'czerwca': '06',
            'lipca': '07',
            'sierpnia': '08',
            'września': '09',
            'października': '10',
            'listopada': '11',
            'grudnia': '12'
        }

        month = months[month]

        return f"{day}/{month}/{year}"


    def parse_schedule(self) -> List[Dict]:
        """Parse schedule data from HTML content"""
        sections = self.soup.find_all('th', class_='gpt-table-section-header')

        for section in sections:
            date = self.__convert_date(section.text.strip())

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

                    time_cell = cells[4].find('tr', class_='text-bold')
                    if not time_cell:
                        continue

                    times = time_cell.text.strip().replace('\xa0', ' ').split(' ')

                    start_time, end_time = times[0].replace('\n', ''), times[2].replace('\n', '')
                    duration = self.__calculate_duration(start_time, end_time)

                    editor = cells[11].text.strip()

                    self.schedule_data.append({
                        'date': date,
                        'program': program,
                        'location': location,
                        'start_time': start_time,
                        'end_time': end_time,
                        'duration': duration,
                        'editor': editor
                    })
                except (AttributeError, IndexError) as e:
                    logging.warning(f"Error parsing row: {e}")
                    continue

        return self.schedule_data

    def save_to_csv(self) -> None:
        """Save parsed schedule to CSV file"""
        headers = ['Data', 'Program', 'Miejsce produkcji', 'Od', 'Do', 'Godziny', 'Montażysta']

        # create output file path
        output_file = self.schedule_config.get_full_output_path()

        # create directory if it doesn't exist
        output_dir = Path(self.schedule_config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
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
                    entry['editor'],
                ])
