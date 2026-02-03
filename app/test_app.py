"""This script will be small, relatively simple tests for the API."""

from unittest.mock import patch, MagicMock

import pytest
from psycopg2 import Error as PsyError

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def build_mock_db(rows):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = rows
    mock_cursor.fetchone.side_effect = lambda: rows[0] if rows else None
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor


@patch('app.psycopg2.connect')
def test_home_page(connect_mock, client):
    response = client.get('/')
    assert response.status_code == 200
    connect_mock.assert_not_called()