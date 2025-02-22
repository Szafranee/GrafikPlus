# GrafikPlus

A simple GUI application for downloading work schedules from the CanalPlus internal system.

[Wersja polska](README.md)

## Quick start

### Users
1. Download the latest version of the program [here](https://github.com/Szafranee/GrafikPlus/releases/download/v1.2.0/GrafikPlus-v1.2.0.exe) or from the [Releases](../../releases) tab
2. Run `GrafikPlus.exe`
3. Enter your login details 
4. Choose the type of schedule and the save location 
5. Click "Pobierz grafik"
6. Done!

### Developers
```bash
git clone https://github.com/Szafranee/GrafikPlus.git
cd grafikplus
pip install -r requirements.txt
python schedule_scraper_gui.py
```

## Features
- Download general and personal schedules
- Week selection via calendar
- Auto-save last used username
- Customizable output location and filename
- Light/dark mode (system-aware)

## Screenshots
![GrafikPlus Dark Mode](https://raw.githubusercontent.com/Szafranee/GrafikPlus/refs/heads/main/img/dark_mode.png)
![GrafikPlus Light Mode](https://raw.githubusercontent.com/Szafranee/GrafikPlus/refs/heads/main/img/light_mode.png)

## System requirements
- Windows 10/11
- Access to a CanalPlus employee account

## Troubleshooting

### Login error
- Verify your credentials
- Make sure you're connected to the Internet

### File saving issues
- Check write permissions in the selected directory
- Make sure the file isn't open in another program

## Technical Details

### Technologies
- Python 3.12
- CustomTkinter (UI)
- BeautifulSoup4 (parsing)
- Requests (data fetching)
- Pandas (Excel export)

### Project Structure
```
grafikplus/
├── schedule_scraper_gui.py   # Main application file
├── schedule_scraper.py       # Scraping logic
├── schedule_parser.py        # HTML parsing
├── config.py                # Configuration
└── requirements.txt         # Dependencies
```
