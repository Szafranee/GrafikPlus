import requests
from bs4 import BeautifulSoup
import pandas as pd
import io
import csv
import os

# Utwórz sesję
session = requests.Session()

# Zdefiniuj dane logowania
payload = {
    'username': '***REMOVED***',
    'password': '***REMOVED***'
}

output_csv_file = 'CanalPlus_grafik.csv'
input_csv_file = 'input.csv'

# Zaloguj się na stronę
login_url = 'https://gpt.canalplus.pl/Account/Login?ReturnUrl=%2f'  # Zastąp prawdziwym adresem URL logowania
session.post(login_url, data=payload)

# Wyślij żądanie GET do strony, z której chcesz odczytać dane
url = 'https://gpt.canalplus.pl/Schedule/Editing?date=02%2F18%2F2024%2000%3A00%3A00'  # Zastąp prawdziwym adresem URL strony
response = session.get(url)

# Użyj BeautifulSoup do analizy odpowiedzi
soup = BeautifulSoup(response.text, 'lxml')

# Znajdź tabelę w odpowiedzi
table = soup.find('table')

# Przekształć tabelę HTML w DataFrame
df = pd.read_html(io.StringIO(str(table)))[0]

# Zapisz DataFrame do pliku CSV
df.to_csv(output_csv_file, index=False)
df.to_csv(input_csv_file, index=False)

# Otwórz pliki wejściowy i wyjściowy
with open(input_csv_file, 'r', encoding='utf-8') as file_in, open(output_csv_file, 'w', newline='', encoding='utf-8') as file_out:
    reader = csv.reader(file_in, delimiter=',', quotechar='"')
    writer = csv.writer(file_out, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    current_date = None
    first_row = True  # Flaga do usunięcia pierwszego wiersza

    for row in reader:
        # Sprawdź, czy wiersz zawiera datę sprawdzając, czy zawiera dzień tygodnia w row[0]
        days_of_week = ['poniedziałek', 'wtorek', 'środa', 'czwartek', 'piątek', 'sobota', 'niedziela']
        if row and any(day in row[0] for day in days_of_week):
            current_date = row[0]
            continue

        # Usuń wiersz, jeśli zaczyna się od "Program"
        if row and row[0].startswith('Program'):
            continue

        # if every cell in the row is the same, skip the row
        if row and len(set(row)) == 1:
            continue

        # Usuń wiersz, jeśli kolumna Montażysta (kolumna 5) jest pusta
        if len(row) >= 6 and row[5].strip() == '':
            continue

        # Zachowaj tylko kolumny 1, 3, 4 i 6
        new_row = [current_date, row[0], row[2], row[3], row[5]]

        # Zastąp separator ';' separatorem ',' wewnątrz cudzysłowów
        for i in range(len(new_row)):
            new_row[i] = new_row[i].replace(';', ',')

        # Zapisz przetworzony wiersz do pliku wyjściowego
        writer.writerow(new_row)

with open(output_csv_file, 'r', encoding='utf-8') as file:
    content = file.read()

# Replace No-Break space with regular space
content = content.replace('\u00A0', ' ')
# Replace double spaces with single space
content = content.replace('  ', ' ')
content = content.replace(' Montaż', '')

with open(output_csv_file, 'w', encoding='utf-8') as file:
    file.write(content)

# Read the file into a list
with open(output_csv_file, 'r', encoding='utf-8') as file:
    lines = file.readlines()

# Add the new line at the beginning of the list
lines.insert(0, "Data;Program;Miejsce produkcji;Od;Do;Godziny;Montażysta\n")

# Write the list back to the file
with open(output_csv_file, 'w', encoding='utf-8') as file:
    file.writelines(lines)

# Read the file into a list
with open(output_csv_file, 'r', encoding='utf-8') as file:
    lines = file.readlines()

    new_lines = []

    for line in lines:
        # skip the first line
        if line.startswith('Data;Program;Miejsce produkcji;Od;Do;Godziny;Montażysta'):
            continue

        # Split the line into a list
        line = line.split(';')

        # Split the time range into start and end times
        start_time, end_time = line[3].split(' - ')

        # Calculate the difference between the start hour and the end hour
        start_hour, start_minute = map(int, start_time.split(':'))
        end_hour, end_minute = map(int, end_time.split(':'))

        # Calculate the duration in hours and minutes
        duration_hours = end_hour - start_hour
        duration_minutes = end_minute - start_minute

        # If the minutes are negative, subtract one hour and add 60 minutes
        if duration_minutes < 0:
            duration_hours -= 1
            duration_minutes += 60

        # If the hours are negative, add 24 hours
        if duration_hours < 0:
            duration_hours += 24

        # Format the duration as "hh:mm"
        duration = f"{duration_hours:02d}:{duration_minutes:02d}"

        # Construct the new line
        new_line = f"{line[0]};{line[1]};{line[2]};{start_time};{end_time};{duration};{line[4]}"
        new_lines.append(new_line)

    # Write the list back to the file
    with open(output_csv_file, 'w', encoding='utf-8') as file:
        file.write('Data;Program;Miejsce produkcji;Od;Do;Godziny;Montażysta\n')
        file.writelines(''.join(new_lines))

os.remove(input_csv_file)