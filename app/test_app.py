"""This script will be small, relatively simple tests for the API."""
# pylint: skip-file
from unittest.mock import patch

from psycopg2 import Error


@patch("app.get_db_connection")
def test_index_db_connection_failure(get_conn_mock, client):
    get_conn_mock.return_value = None

    response = client.get("/")

    assert response.status_code == 500
    assert response.json == {"error": "Database connection failed."}


@patch("app.connect")
def test_index_returns_earthquake(connect_mock, client, earthquake_data, mock_db):
    mock_conn, _ = mock_db([earthquake_data])
    connect_mock.return_value = mock_conn

    response = client.get("/")

    assert response.status_code == 200
    assert response.json == [[earthquake_data]]


@patch("app.connect")
def test_index_db_error_during_query(connect_mock, client, mock_db):
    mock_conn, mock_cursor = mock_db([])

    mock_cursor.execute.side_effect = Error("SQL error")
    connect_mock.return_value = mock_conn

    response = client.get("/")

    assert response.status_code == 500
    assert "SQL error" in response.json["error"]


@patch("app.connect")
def test_get_all_recent_earthquakes(connect_mock, client, earthquake_data, mock_db):
    rows = [earthquake_data]

    mock_conn, mock_cursor = mock_db(rows)
    connect_mock.return_value = mock_conn

    response = client.get("/recent")

    assert response.status_code == 200
    assert response.json == rows

    mock_cursor.execute.assert_called_once()


@patch('app.connect')
def test_get_earthquakes_in_country_found(connect_mock, client, earthquake_data, mock_db):
    mock_conn, mock_cursor = mock_db([earthquake_data])
    connect_mock.return_value = mock_conn

    response = client.get('/America')
    assert response.status_code == 200
    data = response.get_json()
    assert data == earthquake_data
    mock_cursor.execute.assert_called_once()


@patch('app.connect')
def test_get_earthquakes_in_country_not_found(connect_mock, client, mock_db):
    mock_conn, mock_cursor = mock_db([])
    connect_mock.return_value = mock_conn

    response = client.get('/England')
    assert response.status_code == 404
    assert response.get_json() == {"error": "No recent earthquakes here."}
    mock_cursor.execute.assert_called_once()


@patch('app.connect')
def test_get_earthquakes_of_certain_magnitude(connect_mock, client, earthquake_row, mock_db):
    mock_conn, mock_cursor = mock_db([earthquake_row])
    connect_mock.return_value = mock_conn

    mag = earthquake_row['magnitude_value']
    response = client.get(f'/magnitude/{mag}')
    assert response.status_code == 200
    data = response.get_json()
    assert data == [earthquake_row]
    mock_cursor.execute.assert_called_once()


@patch('app.connect')
def test_get_earthquakes_of_certain_magnitude_invalid(connect_mock, client, mock_db):
    mock_conn, mock_cursor = mock_db([])
    connect_mock.return_value = mock_conn

    response = client.get('/magnitude/16.0')
    assert response.status_code == 500
    assert response.get_json() == {"error": "Invalid magnitude value."}


@patch('app.connect')
def test_get_earthquakes_ordered_by_magnitude(connect_mock, client, earthquake_data, mock_db):
    mock_conn, mock_cursor = mock_db(earthquake_data)
    connect_mock.return_value = mock_conn

    response = client.get('/magnitude/desc')
    assert response.status_code == 200
    data = response.get_json()

    assert len(data) == len(earthquake_data)
    assert all(d['magnitude_value'] >= data[i+1]['magnitude_value']
               for i, d in enumerate(data[:-1]))
    mock_cursor.execute.assert_called_once()


@patch('app.connect')
def test_get_earthquakes_ordered_by_magnitude_invalid(connect_mock, client, mock_db):
    mock_conn, mock_cursor = mock_db([])
    connect_mock.return_value = mock_conn

    response = client.get('/magnitude/sideways')
    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid order direction."}
