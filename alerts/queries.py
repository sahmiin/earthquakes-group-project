"""Script containing DB connection and queries"""
from __future__ import annotations

from os import environ as ENV

from psycopg2 import connect, Connection

from .classes import Subscriber


def get_pg_connection() -> Connection:
    """Returns a connection to RDS."""
    return connect(
        host=ENV["HOST_NAME"],
        port=int(ENV.get("PORT", "5432")),
        dbname=ENV["DATABASE_NAME"],
        user=ENV["DATABASE_USERNAME"],
        password=ENV["DATABASE_PASSWORD"],
        connect_timeout=5,
    )


def fetch_subscribers(conn: Connection) -> list[Subscriber]:
    """
    Returns a list of subscribers.
    """
    query = """
        SELECT
            subscriber_id,
            subscriber_name,
            subscriber_email,
            weekly,
            country_id,
            magnitude_value
        FROM earthquakes.subscriber
        WHERE subscriber_email IS NOT NULL;
    """
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()

    subs: list[Subscriber] = []
    for r in rows:
        (
            subscriber_id,
            subscriber_name,
            subscriber_email,
            weekly,
            country_id,
            magnitude_value,
        ) = r

        subs.append(
            Subscriber(
                subscriber_id=int(subscriber_id),
                subscriber_name=str(
                    subscriber_name) if subscriber_name is not None else "",
                subscriber_email=str(subscriber_email),
                weekly=bool(weekly) if weekly is not None else False,
                country_id=int(country_id) if country_id is not None else None,
                magnitude_value=float(
                    magnitude_value) if magnitude_value is not None else None,
            )
        )

    return subs


def fetch_country_name(conn: Connection, country_id: int) -> str:
    """Fetches country name by ID from earthquakes.country."""
    query = """
        SELECT country_name
        FROM earthquakes.country
        WHERE country_id = %s
        LIMIT 1;
    """
    with conn.cursor() as cur:
        cur.execute(query, (country_id,))
        row = cur.fetchone()

    if not row:
        return None
    return str(row[0]) if row[0] is not None else None
