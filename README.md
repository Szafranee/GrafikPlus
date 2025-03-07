# GrafikPlus

Program do pobierania grafików z systemu CanalPlus z prostym interfejsem graficznym.

[English version](README_EN.md)

## Szybki start

### Użytkownicy
1. Pobierz najnowszą wersję programu [tutaj](https://github.com/Szafranee/GrafikPlus/releases/download/v1.2.0/GrafikPlus-v1.2.0.exe) albo z zakładki [Releases](../../releases)
2. Uruchom `GrafikPlus.exe`
3. Wprowadź dane logowania 
4. Wybierz typ grafiku i lokalizację zapisu 
5. Kliknij "Pobierz grafik"
6. Gotowe!

### Programiści
```bash
git clone https://github.com/Szafranee/GrafikPlus.git
cd grafikplus
pip install -r requirements.txt
python schedule_scraper_gui.py
```

## Funkcje
- Pobieranie grafiku montaży oraz grafików osobistych
- Wybór tygodnia przez kalendarz
- Automatyczne zapisywanie ostatnio użytej nazwy użytkownika
- Możliwość wyboru lokalizacji i nazwy pliku wyjściowego
- Tryb jasny/ciemny (zgodny z ustawieniami systemu)

## Zrzuty ekranu
![GrafikPlus Dark Mode](https://raw.githubusercontent.com/Szafranee/GrafikPlus/refs/heads/main/img/dark_mode.png)
![GrafikPlus Light Mode](https://raw.githubusercontent.com/Szafranee/GrafikPlus/refs/heads/main/img/light_mode.png)

## Wymagania systemowe
- Windows 10/11
- Dostęp do konta pracowniczego CanalPlus

## Rozwiązywanie problemów

### Błąd logowania
- Sprawdź poprawność danych logowania
- Upewnij się, że masz połączenie z Internetem

### Problemy z zapisem pliku
- Sprawdź uprawnienia do zapisu w wybranym katalogu
- Upewnij się, że plik nie jest otwarty w innym programie 

## Informacje techniczne

### Użyte technologie
- Python 3.12 
- CustomTkinter (interfejs)
- BeautifulSoup4 (parsowanie)
- Requests (pobieranie danych)
- Pandas (eksport do Excel)

### Struktura projektu
```
grafikplus/
├── schedule_scraper_gui.py   # Główny plik aplikacji
├── schedule_scraper.py       # Logika pobierania danych
├── schedule_parser.py        # Parsowanie HTML
├── config.py                 # Konfiguracja
└── requirements.txt          # Zależności
```
