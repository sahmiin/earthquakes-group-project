"""This script contains tests for the data-related helper functions."""

from unittest.mock import MagicMock, patch

import pandas as pd

from data import fetch_earthquake_data, fetch_subscribers, get_statistics, get_top_countries


@patch("data.pd.read_sql_query")
def test_fetch_earthquake_data(mock_read_sql, df_earthquakes):
    """Test fetching earthquake data returns the correct DataFrame."""
    mock_conn = MagicMock()
    mock_read_sql.return_value = df_earthquakes

    df = fetch_earthquake_data(mock_conn)

    mock_read_sql.assert_called_once()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == len(df_earthquakes)
    assert "country_name" in df.columns
    assert list(df["event_id"]) == list(df_earthquakes["event_id"])


def test_fetch_subscribers(mock_db, fake_subscribers):
    """Test fetching subscriber emails from the database."""

    rows = [(s["subscriber_email"],) for s in fake_subscribers]
    mock_conn, mock_cursor = mock_db(rows)

    emails = fetch_subscribers(mock_conn)

    assert emails == [s["subscriber_email"] for s in fake_subscribers]
    mock_cursor.execute.assert_called_once_with(
        "SELECT subscriber_email FROM subscriber WHERE weekly=true"
    )


def test_get_statistics(df_earthquakes):
    """Test that statistics are computed correctly."""
    stats = get_statistics(df_earthquakes)

    assert stats["total_earthquakes"] == 4
    assert stats["max_magnitude"] == 6.1
    assert stats["average_magnitude"] == round((5.6 + 4.2 + 6.1 + 3.8) / 4, 2)
    assert stats["deepest"] == 15.3
    assert stats["shallowest"] == 5.0
    assert stats["countries_affected"] == 2


def test_get_top_countries(df_earthquakes):
    """Test that top affected countries are returned correctly."""
    top_countries = get_top_countries(df_earthquakes)

    usa_row = top_countries[top_countries["country_name"] == "United States of America"]
    japan_row = top_countries[top_countries["country_name"] == "Japan"]

    assert usa_row["quake_count"].values[0] == 3
    assert japan_row["quake_count"].values[0] == 1

    assert top_countries["quake_count"].tolist() == sorted(
        top_countries["quake_count"], reverse=True
    )
