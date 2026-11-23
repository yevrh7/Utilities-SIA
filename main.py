from app.database.connection import init_db
from app.ui.login_view import LoginWindow
from app.ui.dashboard_view import DashboardWindow


def launch_dashboard(user_id: int, username: str):
    """Launches the main utility dashboard after successful login."""
    dash = DashboardWindow(user_id=user_id, username=username)
    dash.mainloop()


def main():
    # 1. Initialize SQLite tables
    init_db()

    # 2. Launch Login UI
    app = LoginWindow(on_login_success=launch_dashboard)
    app.mainloop()


if __name__ == "__main__":
    main()