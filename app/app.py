"""This script contains a Flask API for real-time earthquake data that technical users may use."""

from os import environ as ENV

import psycopg2
from dotenv import load_dotenv
from flask import Flask, current_app, jsonify, request
from psycopg2.extras import RealDictCursor
from psycopg2 import Error

app = Flask(__name__)

def get_db_connection():
    load_dotenv()
    try:
        connection = psycopg2.connect(
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


@app.route("/", methods=["GET"])
def index():
    """Returns the most recent earthquake."""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed."}), 500

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
                       SELECT * FROM event
                        ORDER BY start_time 
                        LIMIT 1;
                        """)
        most_recent_earthquake = cursor.fetchall()

        return jsonify([dict(most_recent_earthquake)])
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            cursor.close()
            connection.close()


@app.route('/recent')
def get_all_recent_earthquakes():
    """Returns all recent earthquakes in alphabetical order of country name."""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed."}), 500
    
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
                       SELECT * FROM event e
                        JOIN country c ON (e.country_id = c.country_id) 
                        ORDER BY country_name;
                        """)
        earthquakes = cursor.fetchall()
        return jsonify(dict(earthquakes))
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            cursor.close()
            connection.close()


@app.route('/<int:country_name>')
def get_earthquakes_in_country(country_name):
    """Returns recent earthquakes from a given country."""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed."}), 500

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
                       SELECT * FROM event e
                        JOIN country c ON (e.country_id = c.country_id) 
                        WHERE country_name = %s;
                        """, 
                        (country_name,))
        earthquake = cursor.fetchone()
        if earthquake:
            return jsonify(dict(earthquake))
        return jsonify({"error": "No recent earthquakes here."}), 404
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            cursor.close()
            connection.close()


@app.route('/magnitude/<str:order>')
def get_earthquakes_ordered_by_magnitude(order):
    """Returns all recent earthquakes in a given order of magnitude."""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed."}), 500
    
    if order != 'asc' or order != 'desc':
        return jsonify({'error': "Invalid order direction."}), 500
    
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
                       SELECT * FROM event e
                        JOIN country c ON (e.country_id = c.country_id) 
                        ORDER BY magnitude_value %s;
                        """,
                        (order,))
        earthquakes = cursor.fetchall()
        return jsonify(dict(earthquakes))
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            cursor.close()
            connection.close()



@app.route('/magnitude/<int:mag>')
def get_earthquakes_of_certain_magnitude(mag):
    """Returns only earthquakes that are of the given magnitude or higher."""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed."}), 500
    
    if not 0 < mag < 10:
        return jsonify({'error': "Invalid magnitude value."}), 500
    
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
                       SELECT * FROM event e
                        JOIN country c ON (e.country_id = c.country_id) 
                        WHERE magnitude_value >= %s;
                        """,
                        (mag,))
        earthquakes = cursor.fetchall()
        return jsonify(dict(earthquakes))
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            cursor.close()
            connection.close()


if __name__ == "__main__":
    app.config['TESTING'] = True
    app.config['DEBUG'] = True
    app.run(debug=True, host="0.0.0.0", port=5000)
