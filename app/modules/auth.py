import hashlib
import os
import sqlite3
from typing import Optional, Tuple
from app.database.connection import get_connection


def generate_salt() -> str:
    """Generates a secure 16-byte random hex string."""
    return os.urandom(16).hex()


def hash_password(password: str, salt: str) -> str:
    """Combines password and salt using SHA-256."""
    salted_bytes = (password + salt).encode("utf-8")
    return hashlib.sha256(salted_bytes).hexdigest()


def register_user(username: str, password: str) -> Tuple[bool, str]:
    """Validates inputs and saves new user to SQLite with salted hash."""
    clean_username = username.strip()
    if not clean_username or not password:
        return False, "Username and password cannot be empty."

    if len(clean_username) < 3:
        return False, "Username must be at least 3 characters."

    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    salt = generate_salt()
    pwd_hash = hash_password(password, salt)

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                (clean_username, pwd_hash, salt),
            )
            conn.commit()
        return True, "Registration successful! You can now log in."
    except sqlite3.IntegrityError:
        return False, "Username is already taken."
    except Exception as e:
        return False, f"Database error: {str(e)}"


def authenticate_user(username: str, password: str) -> Tuple[bool, Optional[int], str]:
    """
    Verifies user credentials.
    Returns: (is_authenticated, user_id, status_message)
    """
    clean_username = username.strip()
    if not clean_username or not password:
        return False, None, "Please fill in all fields."

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, password_hash, salt FROM users WHERE username = ?",
                (clean_username,),
            )
            user = cursor.fetchone()

        if not user:
            return False, None, "Invalid username or password."

        # Compute hash of entered password using the stored salt
        computed_hash = hash_password(password, user["salt"])

        if computed_hash == user["password_hash"]:
            return True, user["id"], "Login successful."
        else:
            return False, None, "Invalid username or password."

    except Exception as e:
        return False, None, f"Database error: {str(e)}"