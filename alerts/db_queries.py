"""Script containing DB connection and queries"""
from os import environ as ENV

from psycopg2 import connect
from psycopg2.extensions import connection as Connection

from classes import EarthquakeEvent, Subscriber


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
        FROM public.subscriber
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
        FROM public.country
        WHERE country_id = %s
        LIMIT 1;
    """
    with conn.cursor() as cur:
        cur.execute(query, (country_id,))
        row = cur.fetchone()

    if not row:
        return None
    return str(row[0]) if row[0] is not None else None


def fetch_recent_earthquakes(conn: Connection) -> list[EarthquakeEvent]:
    """
    Fetch earthquakes from the last N minutes.
    """
    query = """
        SELECT
            event_id,
            country_id,
            magnitude_value,
            creation_time,
            description,
            longitude,
            latitude
        FROM public.event
        WHERE creation_time >= (NOW() AT TIME ZONE 'utc') - INTERVAL '5 MINUTES'
        ORDER BY creation_time ASC;
    """

    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()

    events: list[EarthquakeEvent] = []
    for event_id, country_id, magnitude_value, creation_time, description, longitude, latitude in rows:

        place_parts = []
        if description:
            place_parts.append(str(description))
        if latitude is not None and longitude is not None:
            place_parts.append(
                f"{float(latitude):.5f}, {float(longitude):.5f}")

        place = " ".join(place_parts) if place_parts else None

        events.append(
            EarthquakeEvent(
                earthquake_id=int(event_id),
                country_id=int(country_id),
                magnitude=float(magnitude_value),
                occurred_at=creation_time.isoformat() if hasattr(
                    creation_time, "isoformat") else str(creation_time),
                place=place,
                country_name=None,
            )
        )

    return events
