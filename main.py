import sys
from app.database.connection import init_db
from app.ui.login_view import LoginWindow


def launch_dashboard(user_id: int, username: str):
    """
    Placeholder for Phase 2: Will launch the ttk.Notebook 3-tab dashboard.
    """
    import tkinter as tk
    from tkinter import ttk

    dash = tk.Tk()
    dash.title("Utilities Suite - Dashboard")
    dash.geometry("800x550")

    header_frame = ttk.Frame(dash, padding=15)
    header_frame.pack(fill="x")

    ttk.Label(
        header_frame,
        text=f"Active User: {username} (ID: {user_id})",
        font=("Segoe UI", 11, "bold"),
    ).pack(side="left")

    ttk.Label(
        dash,
        text="Authentication verified!\nNext step: Loading ttk.Notebook tabs (URL Shortener, Email, Fake Data)",
        font=("Segoe UI", 12),
        justify="center",
    ).pack(expand=True)

    dash.mainloop()


def main():
    # 1. Initialize SQLite tables
    init_db()

    # 2. Launch Login UI
    app = LoginWindow(on_login_success=launch_dashboard)
    app.mainloop()


if __name__ == "__main__":
    main()