"""Helper functions to generate a weekly report of earthquake data."""

import logging
from os import environ as ENV

import pandas as pd
from psycopg2 import connect, Error
from dotenv import load_dotenv
from psycopg2.extensions import connection

logging.basicConfig(level=logging.INFO)

def get_db_connection() -> connection:
    """Returns a database connection."""
    try:
        connection = connect(
            user=ENV.get("DB_USERNAME"),
            password=ENV.get("DB_PASSWORD"),
            host=ENV.get("DB_HOST"),
            port=ENV.get("DB_PORT"),
            database=ENV.get("DB_NAME")
        )
        return connection
    except Error as e:
        logging.warning(f"Error connecting to database: {e}.")
        return None


def fetch_earthquake_data(conn: connection) -> pd.DataFrame:
    """Returns the week's worth of earthquake data as a dataframe."""
    query = """
            SELECT *
            FROM event e 
            JOIN country c
            ON (e.country_id = c.country_id)
            WHERE start_time >= now() - interval '7 days'
            ORDER BY start_time DESC
            """
    with conn:
        df = pd.read_sql_query(query, conn)
    return df


def fetch_subscribers(conn: connection) -> list:
    """Returns the weekly subscriber list."""
    with conn.cursor() as curs:
        curs.execute("SELECT subscriber_email FROM subscribers WHERE weekly=true")
        return [r[0] for r in curs.fetchall()]


def get_statistics(df: pd.DataFrame):
    """Gets main statistics to be used in report."""

    stats = {
        "total_earthquakes": len(df),
        "max_magnitude": df["magnitude_value"].max(),
        "average_magnitude": round(df["magnitude_value"].mean(), 2),
        "deepest": df["depth"].max(),
        "shallowest": df["depth"].min(),
        "countries_affected": df["country_name"].nunique()
    }

    return stats


def get_top_countries(df: pd.DataFrame) -> pd.DataFrame:
    """Returns a dataframe of the top affected countries."""
    return (df.groupby("country_name")
            .size()
            .reset_index(name="quake_count")
            .sort_values("quake_count", ascending=False))
