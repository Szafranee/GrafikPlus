from setuptools import setup

APP = ['schedule_scraper_gui.py']
DATA_FILES = ['favicon.icns']
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'favicon.icns',
    'packages': [
        'customtkinter',
        'tkcalendar',
        'requests',
        'pandas',
        'lxml',
        'openpyxl',
        'python_dotenv'
    ],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)