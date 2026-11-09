import os
import sqlite3

# Resolve path to project root so the .db file sits cleanly in Utilities/
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "utilities_app.db")
SCHEMA_PATH = os.path.join(CURRENT_DIR, "schema.sql")


def get_connection() -> sqlite3.Connection:
    """Connect to SQLite database with Row factory and Foreign Keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    """Reads schema.sql and creates all tables if they don't exist."""
    if not os.path.exists(SCHEMA_PATH):
        raise FileNotFoundError(f"Schema file not found at: {SCHEMA_PATH}")

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_script = f.read()

    with get_connection() as conn:
        conn.executescript(schema_script)
        conn.commit()


if __name__ == "__main__":
    init_db()
    print("Database tables created successfully!")