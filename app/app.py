"""This script contains a Flask API for real-time earthquake data that technical users may use."""

from os import environ as ENV

import psycopg2
from psycopg2 import connect
from dotenv import load_dotenv
from flask import Flask, jsonify
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection
from psycopg2 import Error

app = Flask(__name__)

def get_db_connection() -> connection:
    load_dotenv()
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
        print(f"Error connecting to database: {e}.")
        return None


@app.route("/", methods=["GET"])
def index():
    """Returns the most recent earthquake."""
    connection = get_db_connection()
    if not connection:
        return {"error": "Database connection failed."}, 500

    try:
        with connection.cursor(cursor_factory=RealDictCursor) as curs:
            curs.execute("""
                       SELECT * FROM event
                        ORDER BY start_time 
                        LIMIT 1;
                        """)
            most_recent_earthquake = curs.fetchall()

        return [most_recent_earthquake]
    except Error as e:
        return {"error": str(e)}, 500
    finally:
        if connection:
            connection.close()


@app.route('/recent', defaults={'limit': 20})
@app.route('/recent/<int:limit>')
def get_all_recent_earthquakes(limit):
    """Returns the most recent earthquakes, default 20."""
    connection = get_db_connection()
    if not connection:
        return {"error": "Database connection failed."}, 500

    try:
        with connection.cursor(cursor_factory=RealDictCursor) as curs:
            curs.execute(
                """
                SELECT *
                FROM event e
                JOIN country c ON e.country_id = c.country_id
                ORDER BY start_time DESC
                LIMIT %s;
                """,
                (limit,)
            )
            earthquakes = curs.fetchall()

        return jsonify(earthquakes)

    except Error as e:
        return {"error": str(e)}, 500

    finally:
        if connection:
            connection.close()


@app.route('/<country_name>')
def get_earthquakes_in_country(country_name):
    """Returns recent earthquakes from a given country."""
    connection = get_db_connection()
    if not connection:
        return {"error": "Database connection failed."}, 500

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
                       SELECT * FROM event e
                        JOIN country c ON (e.country_id = c.country_id) 
                        WHERE country_name ILIKE %s;
                        """, 
                        (f"%{country_name}%",))
        earthquake = cursor.fetchone()
        if earthquake:
            return jsonify(earthquake)
        return {"error": "No recent earthquakes here."}, 404
    except Error as e:
        return {"error": str(e)}, 500
    finally:
        if connection:
            cursor.close()
            connection.close()


@app.route('/magnitude/<string:order>')
def get_earthquakes_ordered_by_magnitude(order):
    """Returns all earthquakes in a given order of magnitude."""
    connection = get_db_connection()
    if not connection:
        return {"error": "Database connection failed."}, 500

    order = order.lower()
    if order not in ("asc", "desc"):
        return {"error": "Invalid order direction."}, 400

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        query = f"""
            SELECT *
            FROM event e
            JOIN country c ON e.country_id = c.country_id
            ORDER BY magnitude_value {order.upper()};
        """

        cursor.execute(query)
        earthquakes = cursor.fetchall()
        return jsonify(earthquakes)

    except Error as e:
        return {"error": str(e)}, 500

    finally:
        if connection:
            cursor.close()
            connection.close()


@app.route('/magnitude/<float:mag>')
def get_earthquakes_of_certain_magnitude(mag):
    """Returns only earthquakes that are of the given magnitude or higher."""
    connection = get_db_connection()
    if not connection:
        return {"error": "Database connection failed."}, 500
    
    if not 0 <= float(mag) <= 10:
        return {'error': "Invalid magnitude value."}, 500
    
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
                       SELECT * FROM event e
                        JOIN country c ON (e.country_id = c.country_id) 
                        WHERE magnitude_value = %s;
                        """,
                        (mag,))
        earthquakes = cursor.fetchall()
        return jsonify(earthquakes)
    except Error as e:
        return {"error": str(e)}, 500
    finally:
        if connection:
            cursor.close()
            connection.close()


if __name__ == "__main__":
    app.config['TESTING'] = True
    app.config['DEBUG'] = True
    app.run(debug=True, host="0.0.0.0", port=5000)
