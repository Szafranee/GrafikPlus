import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
import tkcalendar

from config import ScheduleConfig
from schedule_scraper import ScheduleScraper

# Set appearance mode in CustomTkinter (can be "System", "Dark" or "Light")
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class ScheduleScraperGUI:
    """GUI application for downloading schedule using CustomTkinter with dynamic light/dark theming."""

    def __init__(self):
        # Initialize the main window
        self.main_frame = None
        self.scraper = None
        self.root = ctk.CTk()
        self.root.title("GrafikPlus")
        self.root.geometry("600x750")
        self.root.resizable(False, False)
        self.root.after(201, lambda: self.root.iconbitmap('favicon.ico'))

        # Setup theme colors based on the current appearance mode
        self.theme_colors = self._get_theme_colors()

        # File to store the last used username
        self.last_username_file = Path.home() / '.schedule_scraper_user'

        # Create GUI widgets
        self.create_widgets()
        self.center_window()

        # Load the last used username if available
        self._load_last_username()

    @staticmethod
    def _get_theme_colors():
        """
        Determines color settings based on the current appearance mode.
        If the system is in Light mode, use lighter color palette; otherwise, use dark colors.
        """
        mode = ctk.get_appearance_mode()  # Expected to return "Light" or "Dark"
        if mode == "Light":
            return {
                "main_bg": "#F0F0F0",
                "section_bg": "#DADADA",
                "button_download": "#90EE90",  # light green
                "button_exit": "#FF7F7F",      # light red
                "label_fg": "black"
            }
        else:
            return {
                "main_bg": "#3B3B3B",
                "section_bg": "#4B4B4B",
                "button_download": "#b0f090",
                "button_exit": "#f09090",
                "label_fg": "white"
            }

    def _load_last_username(self):
        """Loads the last used username if the file exists."""
        try:
            if self.last_username_file.exists():
                username = self.last_username_file.read_text().strip()
                self.username_entry.delete(0, tk.END)
                self.username_entry.insert(0, username)
        except Exception:
            pass

    def create_widgets(self):
        """Creates and configures all the GUI widgets."""
        # Main frame with fixed margin using theme-specific background
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=8, fg_color=self.theme_colors["main_bg"])
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Login section (credentials)
        self.create_credentials_frame(self.main_frame)

        # Schedule type selection section
        self.create_schedule_selection_frame(self.main_frame)

        # Output file settings section
        self.create_output_frame(self.main_frame)

        # Date selection section (calendar)
        self.create_calendar_frame(self.main_frame)

        # Action buttons section (Download schedule and Exit)
        self.create_button_frame(self.main_frame)

    def create_credentials_frame(self, parent):
        """Creates the section for entering login credentials."""
        cred_frame = ctk.CTkFrame(parent, corner_radius=8, fg_color=self.theme_colors["section_bg"])
        cred_frame.pack(pady=(10, 15), fill="x", padx=10)

        # Section header label
        cred_label = ctk.CTkLabel(
            cred_frame,
            text="Dane logowania",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.theme_colors["label_fg"]
        )
        cred_label.pack(pady=(5, 0))

        # Frame for username input
        username_frame = ctk.CTkFrame(cred_frame, fg_color=self.theme_colors["section_bg"], corner_radius=8)
        username_frame.pack(pady=5, fill="x", padx=10)
        user_label = ctk.CTkLabel(username_frame, text="Nazwa użytkownika:", text_color=self.theme_colors["label_fg"])
        user_label.pack(side="left", padx=(5, 10))
        self.username_entry = ctk.CTkEntry(username_frame, width=300)
        self.username_entry.pack(side="right", padx=(0, 5), pady=5)

        # Frame for password input
        password_frame = ctk.CTkFrame(cred_frame, fg_color=self.theme_colors["section_bg"], corner_radius=8)
        password_frame.pack(pady=5, fill="x", padx=10)
        pass_label = ctk.CTkLabel(password_frame, text="Hasło:", text_color=self.theme_colors["label_fg"])
        pass_label.pack(side="left", padx=(5, 10))
        self.password_entry = ctk.CTkEntry(password_frame, width=300, show="•")
        self.password_entry.pack(side="right", padx=(0, 5), pady=5)

    def create_schedule_selection_frame(self, parent):
        """Creates the section for selecting the schedule type."""
        sel_frame = ctk.CTkFrame(parent, corner_radius=8, fg_color=self.theme_colors["section_bg"])
        sel_frame.pack(pady=(0, 15), fill="x", padx=10)

        # Section header label
        sel_label = ctk.CTkLabel(
            sel_frame,
            text="Wybierz grafik",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.theme_colors["label_fg"]
        )
        sel_label.pack(pady=(5, 0))

        # Frame for radio button
        radio_frame = ctk.CTkFrame(sel_frame, fg_color=self.theme_colors["section_bg"], corner_radius=8)
        radio_frame.pack(pady=5, fill="x", padx=10)

        self.schedule_type = tk.IntVar(value=0)

        general_radio = ctk.CTkRadioButton(
            radio_frame,
            text="Grafik montaży",
            variable=self.schedule_type,
            value=0,
            text_color=self.theme_colors["label_fg"]
        )
        general_radio.pack(side="left", padx=(75, 5), pady=5)

        personal_radio = ctk.CTkRadioButton(
            radio_frame,
            text="Grafik użytkownika",
            variable=self.schedule_type,
            value=1,
            text_color=self.theme_colors["label_fg"]
        )
        personal_radio.pack(side="right", padx=(5, 75), pady=5)


    def create_output_frame(self, parent):
        """Creates the section for output file settings."""
        output_frame = ctk.CTkFrame(parent, corner_radius=8, fg_color=self.theme_colors["section_bg"])
        output_frame.pack(pady=(0, 15), fill="x", padx=10)

        # Section header label
        output_label = ctk.CTkLabel(
            output_frame,
            text="Ustawienia pliku wyjściowego",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.theme_colors["label_fg"]
        )
        output_label.pack(pady=(5, 0))

        # Frame for directory selection
        dir_frame = ctk.CTkFrame(output_frame, fg_color=self.theme_colors["section_bg"], corner_radius=8)
        dir_frame.pack(pady=5, fill="x", padx=10)
        dir_label = ctk.CTkLabel(dir_frame, text="Zapisz w:", text_color=self.theme_colors["label_fg"])
        dir_label.pack(side="left", padx=(5, 10))
        self.output_dir = tk.StringVar(value=str(Path.home() / "Downloads"))
        path_entry = ctk.CTkEntry(dir_frame, textvariable=self.output_dir, width=250)
        path_entry.pack(side="left", padx=(0, 5), pady=5, fill="x", expand=True)
        browse_btn = ctk.CTkButton(dir_frame, text="Browse", command=self.browse_output, width=120)
        browse_btn.pack(side="right", padx=5, pady=5)

        # Frame for file name input
        file_frame = ctk.CTkFrame(output_frame, fg_color=self.theme_colors["section_bg"], corner_radius=8)
        file_frame.pack(pady=5, fill="x", padx=10)
        file_label = ctk.CTkLabel(file_frame, text="Nazwa pliku:", text_color=self.theme_colors["label_fg"])
        file_label.pack(side="left", padx=(5, 10))
        self.filename_entry = ctk.CTkEntry(file_frame, width=250)
        self.filename_entry.pack(side="left", padx=(0, 5), pady=5, fill="x", expand=True)
        self.filename_entry.insert(0, "grafik.csv")

    def create_calendar_frame(self, parent):
        """Creates the date selection section using a calendar widget."""
        cal_container = ctk.CTkFrame(parent, corner_radius=8, fg_color=self.theme_colors["section_bg"])
        cal_container.pack(pady=(0, 5), fill="both", padx=10, expand=True)

        cal_label = ctk.CTkLabel(
            cal_container,
            text="Wybierz dowolny dzień z DOCELOWEGO tygodnia:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.theme_colors["label_fg"]
        )
        cal_label.pack(pady=(5, 0))

        # Embed tkcalendar.Calendar in a CustomTkinter frame
        self.calendar = tkcalendar.Calendar(
            cal_container,
            selectmode="day",
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day,
            background="#2e2e2e",
            foreground="white",
            selectbackground="#3d3d3d",
            selectforeground="white",
            locale="pl_PL"
        )
        self.calendar.pack(pady=5, padx=10, fill="both", expand=True)

    def create_button_frame(self, parent):
        """Creates the section for action buttons."""
        btn_frame = ctk.CTkFrame(parent, fg_color=self.theme_colors["main_bg"], corner_radius=8)
        btn_frame.pack(pady=(5, 5), fill="x", padx=10)

        download_button = ctk.CTkButton(
            btn_frame,
            text="Pobierz grafik",
            command=self.download_schedule,
            width=200,
            fg_color=self.theme_colors["button_download"],
            text_color="black",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        download_button.pack(side="left", padx=10, pady=10, expand=True)

        exit_button = ctk.CTkButton(
            btn_frame,
            text="Wyjście",
            command=self.on_closing,
            width=200,
            fg_color=self.theme_colors["button_exit"],
            text_color="black",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        exit_button.pack(side="right", padx=10, pady=10, expand=True)

    def center_window(self):
        """Centers the application window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def browse_output(self):
        """Handles the selection of the output directory."""
        directory = filedialog.askdirectory(
            initialdir=self.output_dir.get(),
            title="Wybierz katalog docelowy"
        )
        if directory:
            self.output_dir.set(directory)

    def download_schedule(self):
        """Handles the request to download the schedule."""
        username = self.username_entry.get()
        password = self.password_entry.get().strip()

        # Validate login credentials
        if not username or not password:
            messagebox.showerror("Błąd walidacji", "Nazwa użytkownika i hasło nie mogą być puste!")
            return

        # Save the last used username
        try:
            self.last_username_file.write_text(username)
        except Exception:
            pass

        credentials = ScheduleConfig(
            username=username,
            password=password,
            output_dir=self.output_dir.get(),
            output_filename=self.filename_entry.get(),
            selected_date=self.calendar.get_date(),
            is_personal=self.schedule_type.get() == 1
        )

        # TODO: Remove this line after testing
        print(credentials)

        # Initialize the scraper
        self.scraper = ScheduleScraper(credentials)

        # Download the schedule
        scraped = self.scraper.scrape_schedule()
        if scraped:
            self.show_success_message()
        else:
            messagebox.showerror("Error", "Wystąpił błąd podczas pobierania grafiku.\nSprawdź dane logowania i spróbuj ponownie.")

    def on_closing(self):
        """Handles application closing."""
        self.root.destroy()

    def run(self):
        """Starts the main loop of the application."""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    @staticmethod
    def show_success_message():
        """Displays a success message after a successful download."""
        messagebox.showinfo("Sukces", "Grafik pobrany pomyślnie.\nZnajdziesz go w wybranym katalogu.")


if __name__ == "__main__":
    app = ScheduleScraperGUI()
    app.run()