import requests
from typing import Tuple, List, Dict
from app.database.connection import get_connection


def shorten_url(user_id: int, original_url: str) -> Tuple[bool, str]:
    """Shortens a URL via TinyURL's public endpoint and saves it to SQLite."""
    clean_url = original_url.strip()
    if not clean_url:
        return False, "URL cannot be empty."

    if not clean_url.startswith(("http://", "https://")):
        clean_url = "https://" + clean_url

    try:
        response = requests.get(
            "https://tinyurl.com/api-create.php",
            params={"url": clean_url},
            timeout=10,
        )
        if response.status_code != 200 or not response.text.startswith("http"):
            return False, "Failed to shorten URL. Check the link format."

        short_url = response.text.strip()

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO url_records (user_id, original_url, short_url) VALUES (?, ?, ?)",
                (user_id, clean_url, short_url),
            )
            conn.commit()

        return True, short_url

    except requests.RequestException as e:
        return False, f"Network error: {str(e)}"
    except Exception as e:
        return False, f"Database error: {str(e)}"


def get_user_urls(user_id: int) -> List[Dict]:
    """Fetches all shortened URLs belonging to the logged-in user."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT original_url, short_url, created_at
            FROM url_records
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user_id,),
        )
        return [dict(row) for row in cursor.fetchall()]