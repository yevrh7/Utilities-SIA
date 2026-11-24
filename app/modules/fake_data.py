import uuid
from typing import Tuple, List, Dict
from faker import Faker
from app.database.connection import get_connection

fake = Faker()

FIELD_GENERATORS = {
    "full_name": lambda: fake.name(),
    "email": lambda: fake.email(),
    "phone_number": lambda: fake.phone_number(),
    "street_address": lambda: fake.street_address(),
    "city": lambda: fake.city(),
    "country": lambda: fake.country(),
    "birthdate": lambda: str(fake.date_of_birth(minimum_age=18, maximum_age=75)),
    "job_title": lambda: fake.job(),
    "company": lambda: fake.company(),
    "national_id": lambda: fake.ssn(),
}


def generate_mock_profile(selected_fields: List[str]) -> Dict[str, str]:
    """Generates only the selected fields; unselected fields default to '' for SQLite NOT NULL compliance."""
    profile: Dict[str, str] = {}
    for field, generator in FIELD_GENERATORS.items():
        profile[field] = generator() if field in selected_fields else ""
    return profile


def create_and_save_fake_data(
    user_id: int, selected_fields: List[str], count: int = 10
) -> Tuple[bool, List[Dict] | str]:
    """Generates `count` records with only `selected_fields` populated, saves to SQLite, and returns the current batch."""
    if not selected_fields:
        return False, "Select at least one data field to generate."

    if count < 10 or count > 100:
        return False, "Please enter a quantity between 10 and 100."

    batch_id = str(uuid.uuid4())[:8]
    generated_records: List[Dict] = []

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            for _ in range(count):
                profile = generate_mock_profile(selected_fields)
                cursor.execute(
                    """
                    INSERT INTO mock_data_records (
                        user_id, batch_id, full_name, email, phone_number,
                        street_address, city, country, birthdate, job_title,
                        company, national_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        batch_id,
                        profile["full_name"],
                        profile["email"],
                        profile["phone_number"],
                        profile["street_address"],
                        profile["city"],
                        profile["country"],
                        profile["birthdate"],
                        profile["job_title"],
                        profile["company"],
                        profile["national_id"],
                    ),
                )
                profile["batch_id"] = batch_id
                generated_records.append(profile)
            conn.commit()

        return True, generated_records

    except Exception as e:
        return False, f"Database error: {str(e)}"


def get_user_mock_data(user_id: int) -> List[Dict]:
    """Fetches all saved fake data records for the History tab."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT batch_id, full_name, email, phone_number, street_address,
                   city, country, birthdate, job_title, company, national_id, created_at
            FROM mock_data_records
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user_id,),
        )
        return [dict(row) for row in cursor.fetchall()]