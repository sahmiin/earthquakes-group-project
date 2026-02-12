"""This script contains fixtures to be used across all tests in this directory."""
# pylint: skip-file
import os
import tempfile
from unittest.mock import MagicMock

import pytest
import pandas as pd


@pytest.fixture
def mock_db():
    """Builds a mocked psycopg2 connection and cursor."""
    def make_mock_db(rows, cursor_return=True):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = rows
        mock_cursor.fetchone.side_effect = lambda: rows[0] if rows else None

        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.__exit__.return_value = None

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        if cursor_return:
            mock_conn.cursor.return_value = mock_cursor
        return mock_conn, mock_cursor

    return make_mock_db


@pytest.fixture
def df_earthquakes():
    """Returns a fake DataFrame of earthquake data for testing."""
    data = [
        {
            "event_id": 1,
            "usgs_event_id": "2026abcd01",
            "description": "5 km NW of Ridgeway, Alaska",
            "long": -151.158,
            "lat": 60.566,
            "magnitude_value": 5.6,
            "depth": 10.2,
            "start_time": "2026-02-09T12:00:00Z",
            "country_id": 235,
            "country_name": "United States of America"
        },
        {
            "event_id": 2,
            "usgs_event_id": "2026abcd02",
            "description": "10 km SE of Anchorage, Alaska",
            "long": -149.900,
            "lat": 61.218,
            "magnitude_value": 4.2,
            "depth": 5.0,
            "start_time": "2026-02-08T08:30:00Z",
            "country_id": 235,
            "country_name": "United States of America"
        },
        {
            "event_id": 3,
            "usgs_event_id": "2026abcd03",
            "description": "3 km W of Tokyo, Japan",
            "long": 139.6917,
            "lat": 35.6895,
            "magnitude_value": 6.1,
            "depth": 15.3,
            "start_time": "2026-02-07T15:45:00Z",
            "country_id": 392,
            "country_name": "Japan"
        },
        {
            "event_id": 4,
            "usgs_event_id": "2026abcd04",
            "description": "8 km N of Fairbanks, Alaska",
            "long": -147.7164,
            "lat": 64.8378,
            "magnitude_value": 3.8,
            "depth": 7.4,
            "start_time": "2026-02-06T20:10:00Z",
            "country_id": 235,
            "country_name": "United States of America"
        },
    ]
    return pd.DataFrame(data)


@pytest.fixture
def fake_subscribers():
    """Fake subscriber list for testing."""
    return [
        {"subscriber_email": "test1@example.com"},
        {"subscriber_email": "test2@example.com"}
    ]


@pytest.fixture
def temp_pdf():
    """Create a temporary PDF file and clean it up after the test."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.write(b"%PDF-1.4 fake pdf content")
    tmp.close()

    yield tmp.name

    os.unlink(tmp.name)
