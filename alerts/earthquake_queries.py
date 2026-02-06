from __future__ import annotations

from psycopg2.extensions import connection as Connection

from classes import EarthquakeEvent


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
