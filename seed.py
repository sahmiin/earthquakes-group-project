"""This script will seed the master data into the RDS."""

from os import environ as ENV

from psycopg2 import connect, Error
from pycountry import countries
from dotenv import load_dotenv
from psycopg2.extras import execute_values, execute_batch
from psycopg2.extensions import connection

def get_db_connection() -> connection:
    """Returns a database connection."""
    try:
        connection = connect(
            user=ENV.get("DB_USERNAME"),
            password=ENV.get("DB_PASSWORD"),
            host=ENV.get("DB_IP"),
            port=ENV.get("DB_PORT"),
            database=ENV.get("DB_NAME")
        )
        return connection
    except Error as e:
        print(f"Error connecting to database: {e}.")
        return None


def seed_countries(conn: connection) -> None:
    """Seed the countries master data."""
    rows = []

    for c in countries:
        name = getattr(c, "official_name", c.name)
        code = c.alpha_2
        rows.append((name, code))

    try:
        with conn:
            with conn.cursor() as cur:
                execute_batch(cur, 
                            """
                            INSERT INTO country (country_name, country_code)
                            VALUES (%s, %s)
                            ON CONFLICT (country_code) DO NOTHING;
                            """, rows, page_size=100)
        print(f"Seeded {len(rows)} countries.")
    finally:
        conn.close()


def seed_magnitude_types(conn: connection) -> None:
    """Seed magnitude types."""
    magnitude_types = [
        ("ml",),
        ("md",),
        ("mw",),
        ("mb",),
        ("mh",),
        ("mfa",),
        ("mww",),
        ("mwc",),
        ("mwb",),
        ("mwr",),
        ("mint",),
    ]

    sql = """
    INSERT INTO magnitude_type (magnitude_type_name)
    VALUES %s
    ON CONFLICT (magnitude_type_name) DO NOTHING;
    """

    with conn.cursor() as cur:
        execute_values(cur, sql, magnitude_types)

    conn.commit()


if __name__ == "__main__":
    load_dotenv()
    conn = get_db_connection()
    seed_countries(conn)
    seed_magnitude_types(conn)
