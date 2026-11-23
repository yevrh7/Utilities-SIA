import os
import smtplib
from email.message import EmailMessage
from typing import List, Tuple
import requests
from dotenv import load_dotenv
from app.database.connection import get_connection

# Load credentials from environment variables (or replace with your test credentials)
load_dotenv()

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_APP_PASSWORD = os.getenv("SMTP_APP_PASSWORD")
SMS_API_KEY = os.getenv("SMS_API_KEY")

def log_message_to_db(user_id: int, recipient: str, subject: str, status: str) -> None:
    """Saves Email/SMS delivery history into the existing email_logs table."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO email_logs (user_id, recipient, subject, status)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, recipient, subject, status),
        )
        conn.commit()


def get_user_message_logs(user_id: int) -> list:
    """Fetches recent Email/SMS logs for the logged-in user."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT recipient, subject, status, sent_at
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

        log_message_to_db(user_id, recipient, subject, "SENT (Email)")
        return True, "Email sent and logged successfully!"

    except Exception as e:
        log_message_to_db(user_id, recipient, subject, "FAILED (Email)")
        return False, f"Email failed: {str(e)}"


def send_sms(user_id: int, phone_number: str, message: str) -> Tuple[bool, str]:
    """Sends an SMS via Semaphore REST API and logs the result to SQLite."""
    phone_number = phone_number.strip()

    if len(phone_number) < 10:
        return False, "Please enter a valid mobile number (e.g., 09171234567)."

    try:
        url = "https://api.semaphore.co/api/v4/messages"
        payload = {
            "apikey": SMS_API_KEY,
            "number": phone_number,
            "message": message,
        }
        response = requests.post(url, data=payload, timeout=15)
        response.raise_for_status()

        log_message_to_db(user_id, phone_number, "[SMS Message]", "SENT (SMS)")
        return True, "SMS sent and logged successfully!"

    except Exception as e:
        log_message_to_db(user_id, phone_number, "[SMS Message]", "FAILED (SMS)")
        return False, f"SMS failed: {str(e)}"