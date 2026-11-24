import os
import smtplib
from email.message import EmailMessage
from typing import Tuple
import requests
from dotenv import load_dotenv
from app.database.connection import get_connection

load_dotenv()

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_APP_PASSWORD = os.getenv("SMTP_APP_PASSWORD")
TEXTBEE_API_KEY = os.getenv("TEXTBEE_API_KEY")
TEXTBEE_DEVICE_ID = os.getenv("TEXTBEE_DEVICE_ID")


def _ensure_body_column() -> None:
    """Safely adds the 'body' column to existing email_logs tables without breaking old .db files."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(email_logs)")
        columns = [row[1] for row in cursor.fetchall()]
        if "body" not in columns:
            cursor.execute("ALTER TABLE email_logs ADD COLUMN body TEXT DEFAULT ''")
            conn.commit()


def log_message_to_db(user_id: int, recipient: str, subject: str, body: str, status: str) -> None:
    """Saves Email/SMS delivery history (including message body) into email_logs."""
    _ensure_body_column()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO email_logs (user_id, recipient, subject, body, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, recipient, subject, body, status),
        )
        conn.commit()


def get_user_message_logs(user_id: int) -> list:
    """Fetches recent Email/SMS logs for the logged-in user."""
    _ensure_body_column()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT recipient, subject, body, status, sent_at
            FROM email_logs
            WHERE user_id = ?
            ORDER BY sent_at DESC
            LIMIT 20
            """,
            (user_id,),
        )
        return cursor.fetchall()


def send_email(user_id: int, recipient: str, subject: str, body: str) -> Tuple[bool, str]:
    """Sends an email via Gmail SMTP and logs the result to SQLite."""
    if not SMTP_EMAIL or not SMTP_APP_PASSWORD:
        return False, "Missing SMTP credentials. Please check your .env file."

    recipient = recipient.strip()
    subject = subject.strip() or "(No Subject)"

    if "@" not in recipient or "." not in recipient:
        return False, "Please enter a valid recipient email address."

    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = SMTP_EMAIL
        msg["To"] = recipient

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
            smtp.send_message(msg)

        log_message_to_db(user_id, recipient, subject, body, "SENT (Email)")
        return True, "Email sent and logged successfully!"

    except Exception as e:
        log_message_to_db(user_id, recipient, subject, body, "FAILED (Email)")
        return False, f"Email failed: {str(e)}"


def send_sms(user_id: int, phone_number: str, message: str) -> Tuple[bool, str]:
    """Sends an SMS via TextBee Android Gateway API and logs the result to SQLite."""
    if not TEXTBEE_API_KEY or not TEXTBEE_DEVICE_ID:
        return False, "Missing TextBee credentials. Please check your .env file."

    clean_num = phone_number.strip().replace(" ", "").replace("-", "")
    if clean_num.startswith("09") and len(clean_num) == 11:
        clean_num = "+63" + clean_num[1:]
    elif not clean_num.startswith("+"):
        return False, "Enter a valid 11-digit PH number (e.g., 09171234567) or +63 format."

    try:
        url = f"https://api.textbee.dev/api/v1/gateway/devices/{TEXTBEE_DEVICE_ID}/send-sms"
        headers = {"x-api-key": TEXTBEE_API_KEY}
        payload = {
            "recipients": [clean_num],
            "message": message,
        }

        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()

        log_message_to_db(user_id, clean_num, "[SMS Message]", message, "SENT (SMS)")
        return True, "SMS queued to your phone via TextBee and logged!"

    except Exception as e:
        log_message_to_db(user_id, clean_num, "[SMS Message]", message, "FAILED (SMS)")
        return False, f"SMS failed: {str(e)}"