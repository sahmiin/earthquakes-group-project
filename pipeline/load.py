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


def get_location_id():
    with conn.cursor() as cur:
        cur.execute("SELECT country_name, country_id FROM country;")
        country_codes_lookup = dict(cur.fetchall())

    key = ENV["API_KEY"]
    geocoder = OpenCageGeocode(key)
    for e in new_events:
        result = geocoder.reverse_geocode(e["latitude"], e["longitude"])
        country = result[0]["components"]["country"]
        e["country_id"] = country_codes_lookup[country]


def upload_data(conn, new_events):
    upsert_query = """
    INSERT INTO earthquake_event (usgs_event_id, start_time, description, 
    creation_time, depth, depth_uncertainty, used_phase_count, used_station_count, 
    azimuthal_gap, magnitude_value, magnitude_uncertainty, magnitude_type_id,
    country_id, latitude, longitude)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
        earthquake_event.start_time              IS DISTINCT FROM EXCLUDED.start_time              OR
        earthquake_event.description             IS DISTINCT FROM EXCLUDED.description             OR
        earthquake_event.creation_time           IS DISTINCT FROM EXCLUDED.creation_time           OR
        earthquake_event.depth                   IS DISTINCT FROM EXCLUDED.depth                   OR
        earthquake_event.depth_uncertainty       IS DISTINCT FROM EXCLUDED.depth_uncertainty       OR
        earthquake_event.used_phase_count        IS DISTINCT FROM EXCLUDED.used_phase_count        OR
        earthquake_event.used_station_count      IS DISTINCT FROM EXCLUDED.used_station_count      OR
        earthquake_event.azimuthal_gap           IS DISTINCT FROM EXCLUDED.azimuthal_gap           OR
        earthquake_event.magnitude_value         IS DISTINCT FROM EXCLUDED.magnitude_value         OR
        earthquake_event.magnitude_uncertainty   IS DISTINCT FROM EXCLUDED.magnitude_uncertainty   OR
        earthquake_event.magnitude_type_id       IS DISTINCT FROM EXCLUDED.magnitude_type_id       OR
        earthquake_event.country_id              IS DISTINCT FROM EXCLUDED.country_id              OR
        earthquake_event.latitude                IS DISTINCT FROM EXCLUDED.latitude                OR
        earthquake_event.longitude               IS DISTINCT FROM EXCLUDED.longitude;
    """

    with conn.cursor() as cur:
        cur.executemany(upsert_query, new_events)
    conn.commit()


if __name__ == "__main__":
    load_dotenv()
    conn = get_connection(ENV)
    events = get_magnitude_type_id(conn)
    events = get_location_id(conn, events)
    upload_data()
