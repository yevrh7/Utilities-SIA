import tkinter as tk
from tkinter import ttk
from app.ui.messaging_view import MessagingFrame
from app.ui.url_shortener_view import UrlShortenerFrame

class DashboardWindow(tk.Tk):
    def __init__(self, user_id: int, username: str):
        super().__init__()
        self.user_id = user_id
        self.username = username

        self.title("Utilities Suite - Dashboard")
        self.geometry("850x600")
        self.minsize(750, 520)

        self._configure_styles()
        self._build_ui()

    def _configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))
        style.configure("SubHeader.TLabel", font=("Segoe UI", 11, "bold"))
        style.configure("TButton", font=("Segoe UI", 10), padding=6)

    def _build_ui(self):
        # --- Top Navigation Bar ---
        top_bar = ttk.Frame(self, padding=(20, 15))
        top_bar.pack(fill="x")

        ttk.Label(
            top_bar,
            text=f"Welcome, {self.username}",
            style="Header.TLabel",
        ).pack(side="left")

        # Utility Selector ComboBox (Created here, but NOT packed yet so it stays hidden initially)
        self.selector_frame = ttk.Frame(top_bar)

        ttk.Label(self.selector_frame, text="Switch Utility:").pack(side="left", padx=(0, 8))

        self.utility_options = [
            "SMS and Email Sender",
            "URL Shortener",
            "Fake Data Generator",
        ]
        self.utility_combo = ttk.Combobox(
            self.selector_frame,
            values=self.utility_options,
            state="readonly",
            width=25,
            font=("Segoe UI", 10),
        )
        self.utility_combo.pack(side="left")
        self.utility_combo.bind("<<ComboboxSelected>>", self._on_utility_selected)

        ttk.Separator(self, orient="horizontal").pack(fill="x")

        # --- Dynamic Content Area ---
        self.content_area = ttk.Frame(self, padding=20)
        self.content_area.pack(fill="both", expand=True)

        # Initialize all 3 utility views
        self.views = {
            "SMS and Email Sender": MessagingFrame(self.content_area, self.user_id),
            "URL Shortener": UrlShortenerFrame(self.content_area, self.user_id),
            "Fake Data Generator": self._create_placeholder_frame(
                "Fake Data Generator", "Ready for 10-field Faker module integration."
            ),
        }

        # Show initial welcome menu
        self._show_welcome_menu()

    def _show_welcome_menu(self):
        # Ensure top-right dropdown is hidden on the welcome screen
        self.selector_frame.pack_forget()

        self.welcome_frame = ttk.Frame(self.content_area)
        self.welcome_frame.pack(expand=True)

        ttk.Label(
            self.welcome_frame,
            text="Choose a Utility to Get Started",
            style="Header.TLabel",
        ).pack(pady=(0, 10))

        ttk.Label(
            self.welcome_frame,
            text="Select an option below to launch a tool.",
        ).pack(pady=(0, 25))

        for option in self.utility_options:
            btn = ttk.Button(
                self.welcome_frame,
                text=option,
                width=32,
                command=lambda opt=option: self._select_utility(opt),
            )
            btn.pack(pady=6)

    def _create_placeholder_frame(self, title: str, subtitle: str) -> ttk.Frame:
        frame = ttk.Frame(self.content_area)
        ttk.Label(frame, text=title, style="Header.TLabel").pack(pady=(40, 10))
        ttk.Label(frame, text=subtitle).pack()
        return frame

    def _select_utility(self, selection: str):
        self.utility_combo.set(selection)
        self._switch_view(selection)

    def _on_utility_selected(self, event):
        selection = self.utility_combo.get()
        self._switch_view(selection)

    def _switch_view(self, selection: str):
        # Hide welcome screen if visible
        if hasattr(self, "welcome_frame") and self.welcome_frame.winfo_exists():
            self.welcome_frame.pack_forget()

        # Reveal the top-right dropdown now that the user is inside a tool
        if not self.selector_frame.winfo_ismapped():
            self.selector_frame.pack(side="right")

        # Hide all utility frames
        for frame in self.views.values():
            frame.pack_forget()

        # Display the chosen utility frame
        target_frame = self.views.get(selection)
        if target_frame:
            target_frame.pack(fill="both", expand=True)