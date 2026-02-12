"""This script contains fixtures for testing the API script."""
# pylint: skip-file
import pytest
from unittest.mock import MagicMock
from app import app


@pytest.fixture
def client():
    """Mock Flask test client for calling API endpoints."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_db():
    """Builds a mocked psycopg2 connection and cursor."""
    def make_mock_db(rows):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = rows
        mock_cursor.fetchone.side_effect = lambda: rows[0] if rows else None

        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.__exit__.return_value = None

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        return mock_conn, mock_cursor

    return make_mock_db


@pytest.fixture
def earthquake_row():
    """Fake earthquake data (single row) for testing."""
    return {
        "event_id": 2,
        "usgs_event_id":'2026coutco',
        "description":'5 km NW of Ridgeway, Alaska',
        "long":-151.158,
        "lat":60.566,
        "magnitude_value": 5.6,
        "start_time": "2026-02-09T12:00:00Z",
        "country_id": 235,
        "country_name": "United States of America"
    }

@pytest.fixture
def earthquake_data():
    """Fake earthquake data (multiple rows) for testing."""
    return [{
        "event_id": 2,
        "usgs_event_id":'2026coutco',
        "description":'5 km NW of Ridgeway, Alaska',
        "long":-151.158,
        "lat":60.566,
        "magnitude_value": 5.6,
        "start_time": "2026-02-09T12:00:00Z",
        "country_id": 235,
        "country_name": "United States of America"
    },
            {
        "event_id": 3,
        "usgs_event_id":'2026coutco',
        "description":'5 km NW of Ridgeway, Alaska',
        "long":45.43,
        "lat":-60.566,
        "magnitude_value": 2.3,
        "start_time": "2026-02-09T12:00:00Z",
        "country_id": 2,
        "country_name": "Islamic Republic of Afghanistan"
    },
    ]