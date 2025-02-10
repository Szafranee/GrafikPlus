import csv
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

from bs4 import BeautifulSoup


class ScheduleParser:
    def __init__(self, html_content: str, credentials):
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.schedule_data = []
        self.credentials = credentials

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

                    time_cell = cells[4].find('tr', class_='text-bold')
                    if not time_cell:
                        continue

                    times = time_cell.text.strip().replace('\xa0', ' ').split(' ')

                    start_time, end_time = times[0].replace('\n', ''), times[2].replace('\n', '')
                    duration = self.__calculate_duration(start_time, end_time)

                    remarks_cell = row.find('pre', class_='gpt-pre-remarks')
                    remarks = remarks_cell.text.strip() if remarks_cell else ""

                    editor = cells[11].text.strip()

                    self.schedule_data.append({
                        'date': date,
                        'program': program,
                        'location': location,
                        'start_time': start_time,
                        'end_time': end_time,
                        'duration': duration,
                        'editor': editor,
                        'remarks': remarks
                    })
                except (AttributeError, IndexError) as e:
                    logging.warning(f"Error parsing row: {e}")
                    continue

        return self.schedule_data

    def save_to_csv(self) -> None:
        """Save parsed schedule to CSV file"""
        headers = ['Data', 'Program', 'Miejsce produkcji', 'Od', 'Do', 'Godziny', 'Montażysta', 'Uwagi']

        # create output file path
        output_file = self.credentials["output_dir"] + '/' + self.credentials["output_filename"]

        # create directory if it doesn't exist
        output_dir = Path(self.credentials["output_dir"])
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
                    entry['remarks']
                ])
