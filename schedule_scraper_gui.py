import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import ttk, filedialog

import tkcalendar
from ttkthemes import ThemedTk

from schedule_scraper import ScheduleScraper


class ScheduleScraperGUI:
    """GUI application for schedule scraping with dark theme"""

    def __init__(self):
        # Initialize main window with dark theme
        self.scraper = None
        self.root = ThemedTk(theme="equilux")
        self.root.title("Schedule Scraper")
        self.root.geometry("600x550")
        self.root.resizable(False, False)  # Disable window resizing

        # Load last username if exists
        self.last_username_file = Path.home() / '.schedule_scraper_user'

        # Create GUI elements
        self.create_widgets()
        self.center_window()

        # Load last username
        self._load_last_username()

    def _load_last_username(self):
        """Load last used username if exists"""
        try:
            if self.last_username_file.exists():
                username = self.last_username_file.read_text().strip()
                self.username_entry.delete(0, tk.END)
                self.username_entry.insert(0, username)
        except Exception:
            pass

    def create_widgets(self):
        """Create and configure all GUI widgets"""
        # Main container with fixed padding
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Credentials section
        self._create_credentials_frame(main_frame)

        # Output settings section
        self._create_output_frame(main_frame)

        # Calendar section
        self._create_calendar_frame(main_frame)

        # Action buttons
        self._create_button_frame(main_frame)

    def _create_credentials_frame(self, parent):
        """Create credentials input section"""
        cred_frame = ttk.LabelFrame(parent, text="Dane logowania", padding=10)
        cred_frame.pack(fill=tk.X, pady=(0, 15))

        # Username
        username_frame = ttk.Frame(cred_frame)
        username_frame.pack(fill=tk.X, pady=5)
        ttk.Label(username_frame, text="Nazwa użytkownika:").pack(side=tk.LEFT)
        self.username_entry = ttk.Entry(username_frame, width=40)
        self.username_entry.pack(side=tk.RIGHT, padx=5)

        # Password
        password_frame = ttk.Frame(cred_frame)
        password_frame.pack(fill=tk.X, pady=5)
        ttk.Label(password_frame, text="Hasło:").pack(side=tk.LEFT)
        self.password_entry = ttk.Entry(password_frame, width=40, show="•")
        self.password_entry.pack(side=tk.RIGHT, padx=5)

    def _create_output_frame(self, parent):
        """Create output settings section"""
        file_frame = ttk.LabelFrame(parent, text="Ustawienia pliku wyjściowego", padding=10)
        file_frame.pack(fill=tk.X, pady=(0, 15))

        # Directory selection
        dir_frame = ttk.Frame(file_frame)
        dir_frame.pack(fill=tk.X, pady=5)
        ttk.Label(dir_frame, text="Zapisz w:").pack(side=tk.LEFT)
        self.output_dir = tk.StringVar(value=str(Path.home() / "Downloads"))
        path_entry = ttk.Entry(dir_frame, textvariable=self.output_dir, width=30)
        path_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        browse_btn = ttk.Button(dir_frame, text="Przeglądaj", command=self.browse_output)
        browse_btn.pack(side=tk.RIGHT)

        # Filename
        file_name_frame = ttk.Frame(file_frame)
        file_name_frame.pack(fill=tk.X, pady=5)
        ttk.Label(file_name_frame, text="Nazwa pliku:").pack(side=tk.LEFT)
        self.filename_entry = ttk.Entry(file_name_frame, width=30)
        self.filename_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.filename_entry.insert(0, 'schedule.csv')

    def _create_calendar_frame(self, parent):
        """Create calendar selection section"""
        cal_frame = ttk.LabelFrame(parent, text="Wybierz dowolny dzień z docelowego tygodnia:", padding=10)
        cal_frame.pack(fill=tk.BOTH, pady=(0, 15))

        self.calendar = tkcalendar.Calendar(
            cal_frame,
            selectmode='day',
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day,
            background="#2e2e2e",
            foreground="white",
            selectbackground="#3d3d3d",
            selectforeground="white",
            locale='pl_PL'
        )
        self.calendar.pack(expand=True, fill=tk.BOTH)

    def _create_button_frame(self, parent):
        """Create action buttons section"""
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        download_btn = ttk.Button(btn_frame, text="Pobierz grafik", command=self.download_schedule, width=30)
        download_btn.pack(side=tk.LEFT, padx=5, expand=True,)

        exit_btn = ttk.Button(btn_frame, text="Wyjście", command=self.on_closing, width=30)
        exit_btn.pack(side=tk.RIGHT, padx=5, expand=True)

    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def browse_output(self):
        """Handle output directory selection"""
        directory = filedialog.askdirectory(
            initialdir=self.output_dir.get(),
            title="Wybierz katalog wyjściowy"
        )
        if directory:
            self.output_dir.set(directory)

    def download_schedule(self):
        """Handle schedule download request"""
        username = self.username_entry.get()
        password = self.password_entry.get().strip()

        # Validate required fields
        if not username or not password:
            tk.messagebox.showerror(
                "Błąd walidacji",
                "Nazwa użytkownika i hasło nie mogą być puste!"
            )
            return

        # Save username for next time
        try:
            self.last_username_file.write_text(username)
        except Exception:
            pass

        credentials = {
            'username': username,
            'password': password,
            'output_dir': self.output_dir.get(),
            'output_filename': self.filename_entry.get(),
            'selected_date': self.calendar.get_date()
        }

        print(credentials)

        # Initialize scraper
        self.scraper = ScheduleScraper(credentials)

        # Scrape schedule
        scraped = self.scraper.scrape_schedule()
        if scraped:
            self.show_success_message()
        else:
            tk.messagebox.showerror("Błąd", "Wystąpił błąd podczas pobierania grafiku.f\nSprawdź dane logowania i spróbuj ponownie.")


    def on_closing(self):
        """Handle application closing"""
        self.root.destroy()

    def run(self):
        """Start the GUI application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    @staticmethod
    def show_success_message():
        """Display success message after scraping"""
        success_message = "Pomyślnie pobrano grafik.\n" \
                          "Znajdziesz go w wybranym katalogu."
        tk.messagebox.showinfo("Sukces", success_message)


if __name__ == "__main__":
    app = ScheduleScraperGUI()
    app.run()
