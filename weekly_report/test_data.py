"""Simple tests for the helper functions of this report."""

from unittest.mock import MagicMock, patch

import pytest
import pandas as pd

from data import get_db_connection, fetch_earthquake_data, fetch_subscribers, get_statistics, get_top_countries

@patch(get_db_connection)
def test_db_connection_success(mock_connection):
    mock_conn = MagicMock()
    mock_connection.return_value = mock_conn

    conn = get_db_connection()

    assert conn is mock_conn
    mock_connection.assert_called_once()