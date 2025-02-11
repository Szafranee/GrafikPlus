import csv
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

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

    @staticmethod
    def __is_date_row(row) -> bool:
        """Check if the row contains a date header"""
        return bool(row.find('th', class_='gpt-table-section-header'))

    def __get_date_from_row(self, row) -> Optional[str]:
        """Extract and convert date from a date row"""
        date_header = row.find('th', class_='gpt-table-section-header')
        if date_header:
            return self.__convert_date(date_header.text.strip())
        return None

    def parse_general_schedule(self) -> List[Dict]:
        """Parse schedule data from HTML content with sequential row processing"""
        current_date = None
        all_rows = self.soup.find_all('tr')

        for row in all_rows:
            # Check if this is a date row
            if self.__is_date_row(row):
                current_date = self.__get_date_from_row(row)
                continue

            # Skip rows without date context
            if not current_date:
                continue

            cells = row.find_all('td')
            if not cells:
                continue

            program_cell = row.find('span')
            if not program_cell:
                continue

            try:
                program = program_cell.text.strip()

                time_cell = cells[4].find('tr', class_='text-bold')
                if not time_cell:
                    continue

                times = time_cell.text.strip().replace('\xa0', ' ').split(' ')
                start_time = times[0].replace('\n', '')
                end_time = times[2].replace('\n', '')
                duration = self.__calculate_duration(start_time, end_time)
                editor = cells[11].text.strip()

                self.schedule_data.append({
                    'date': current_date,
                    'program': program,
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': duration,
                    'editor': editor
                })
            except AttributeError as e:
                logging.warning(f"Error parsing row: {e}")
                continue
            except IndexError:
                continue

        return self.schedule_data

    def parse_personal_schedule(self) -> List[Dict]:
        """Parse personal schedule data with sequential row processing"""
        current_date = None
        all_rows = self.soup.find_all('tr')

        for row in all_rows:
            # Check if this is a date row
            if self.__is_date_row(row):
                current_date = self.__get_date_from_row(row)
                continue

            # Skip rows without date context
            if not current_date:
                continue

            try:
                # Find program name from the nested table structure
                program_table = row.find('td')
                if not program_table:
                    continue

                program_table = program_table.find('table')
                if not program_table:
                    continue

                program_cell = program_table.find('span')
                if not program_cell:
                    continue

                program = program_cell.text.strip()

                # Find time information
                time_cell = row.find('span', class_='text-bold')
                if not time_cell:
                    continue

                # Parse time information
                times = time_cell.text.strip().split('-')
                if len(times) != 2:
                    continue

                start_time = times[0].strip().replace('\xa0', '')
                end_time = times[1].strip().replace('\xa0', '')
                duration = self.__calculate_duration(start_time, end_time)

                self.schedule_data.append({
                    'date': current_date,
                    'program': program,
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': duration
                })
            except (AttributeError, IndexError) as e:
                logging.warning(f"Error parsing row: {e}")
                continue

        return self.schedule_data

    def parse_schedule(self) -> None:
        """Parse schedule data from HTML content"""
        if self.schedule_config.is_personal:
            self.parse_personal_schedule()
        else:
            self.parse_general_schedule()

    def save_to_csv(self) -> None:
        """Save parsed schedule to CSV file"""
        headers = ['Data', 'Program', 'Od', 'Do', 'Godziny'] if self.schedule_config.is_personal \
            else ['Data', 'Program', 'Od', 'Do', 'Godziny', 'Montażysta']

        output_file = self.schedule_config.get_full_output_path()
        output_dir = Path(self.schedule_config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(headers)

            if self.schedule_config.is_personal:
                for entry in self.schedule_data:
                    writer.writerow([
                        entry['date'],
                        entry['program'],
                        entry['start_time'],
                        entry['end_time'],
                        entry['duration'],
                    ])
            else:
                for entry in self.schedule_data:
                    writer.writerow([
                        entry['date'],
                        entry['program'],
                        entry['start_time'],
                        entry['end_time'],
                        entry['duration'],
                        entry['editor'],
                    ])
