from os import environ as ENV, _Environ
from dotenv import load_dotenv
import psycopg2
from opencage.geocoder import OpenCageGeocode


def get_connection(config: _Environ):
    """Connection to RDS instance"""
    conn = psycopg2.connect(
        user=config["DB_USERNAME"],
        password=config["DB_PASSWORD"],
        host=config["HOST_NAME"],
        database=config["DB_NAME"],
        port=config["PORT"]
    )
    return conn


def get_magnitude_type_id(conn, new_events):
    """Map magnitude type name to the id stored in the database"""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT magnitude_type_name, magnitude_type_id FROM magnitude_type;")
        mag_type_table = dict(cur.fetchall())
        for e in new_events:
            e["magnitude_type_id"] = mag_type_table[e["magnitude_type_name"]]

    return new_events


def get_location_id(conn, new_events):
    """Uses a geolocation API to return the country code for a given lat and lon"""
    with conn.cursor() as cur:
        cur.execute("SELECT country_code, country_id FROM country;")
        country_codes_lookup = dict(cur.fetchall())

    existing_event_countries = get_existing_event_countries(conn, new_events)

    key = ENV["API_KEY"]
    geocoder = OpenCageGeocode(key)

    for e in new_events:
        event_id = e["usgs_event_id"]
        if event_id in existing_event_countries:
            e["country_id"] = existing_event_countries[event_id]
            continue

        result = geocoder.reverse_geocode(e["latitude"], e["longitude"])
        components = result[0].get("components", {})
        country_code = components.get("country_code")

        if not country_code:
            e["country_id"] = country_codes_lookup["IW"]
        else:
            e["country_id"] = country_codes_lookup[country_code.upper()]

    return new_events


def get_existing_event_countries(conn, new_events):
    """Selects all event ids and country ids already in the database"""
    event_ids = [e["usgs_event_id"] for e in new_events]

    if not event_ids:
        return {}

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT usgs_event_id, country_id
            FROM event
            WHERE usgs_event_id = ANY(%s);
            """,
            (event_ids,)
        )
        return dict(cur.fetchall())


def upload_data(conn, new_events):
    """SQL query to add all events to DB"""
    upsert_query = """
    INSERT INTO event (usgs_event_id, start_time, description, 
    creation_time, depth, depth_uncertainty, used_phase_count, used_station_count, 
    azimuthal_gap, magnitude_value, magnitude_uncertainty, magnitude_type_id,
    country_id, latitude, longitude)
    VALUES (%(usgs_event_id)s,
        %(start_time)s,
        %(description)s,
        %(creation_time)s,
        %(depth_value)s,
        %(depth_uncertainty)s,
        %(used_phase_count)s,
        %(used_station_count)s,
        %(azimuthal_gap)s,
        %(magnitude_value)s,
        %(magnitude_uncertainty)s,
        %(magnitude_type_id)s,
        %(country_id)s,
        %(latitude)s,
        %(longitude)s)
    ON CONFLICT (usgs_event_id) DO UPDATE SET
        start_time            = EXCLUDED.start_time,
        description           = EXCLUDED.description,
        creation_time         = EXCLUDED.creation_time,
        depth                 = EXCLUDED.depth,
        depth_uncertainty     = EXCLUDED.depth_uncertainty,
        used_phase_count      = EXCLUDED.used_phase_count,
        used_station_count    = EXCLUDED.used_station_count,
        azimuthal_gap         = EXCLUDED.azimuthal_gap,
        magnitude_value       = EXCLUDED.magnitude_value,
        magnitude_uncertainty = EXCLUDED.magnitude_uncertainty,
        magnitude_type_id     = EXCLUDED.magnitude_type_id,
        country_id            = EXCLUDED.country_id,
        latitude              = EXCLUDED.latitude,
        longitude             = EXCLUDED.longitude
    WHERE
        event.start_time              IS DISTINCT FROM EXCLUDED.start_time              OR
        event.description             IS DISTINCT FROM EXCLUDED.description             OR
        event.creation_time           IS DISTINCT FROM EXCLUDED.creation_time           OR
        event.depth                   IS DISTINCT FROM EXCLUDED.depth                   OR
        event.depth_uncertainty       IS DISTINCT FROM EXCLUDED.depth_uncertainty       OR
        event.used_phase_count        IS DISTINCT FROM EXCLUDED.used_phase_count        OR
        event.used_station_count      IS DISTINCT FROM EXCLUDED.used_station_count      OR
        event.azimuthal_gap           IS DISTINCT FROM EXCLUDED.azimuthal_gap           OR
        event.magnitude_value         IS DISTINCT FROM EXCLUDED.magnitude_value         OR
        event.magnitude_uncertainty   IS DISTINCT FROM EXCLUDED.magnitude_uncertainty   OR
        event.magnitude_type_id       IS DISTINCT FROM EXCLUDED.magnitude_type_id       OR
        event.country_id              IS DISTINCT FROM EXCLUDED.country_id              OR
        event.latitude                IS DISTINCT FROM EXCLUDED.latitude                OR
        event.longitude               IS DISTINCT FROM EXCLUDED.longitude;
    """

    with conn.cursor() as cur:
        cur.executemany(upsert_query, new_events)
    conn.commit()


def run_load_script(new_events: list[dict]):
    """Script to run necessary functions to load new events to the DB"""
    load_dotenv()
    conn = get_connection(ENV)
    try:
        events_mag_id = get_magnitude_type_id(conn, new_events)
        events_location_id = get_location_id(conn, events_mag_id)
        upload_data(conn, events_location_id)
    finally:
        conn.close()


if __name__ == "__main__":
    run_load_script()
