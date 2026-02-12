"""Test script with pytest for the load script"""

# pylint: skip-file

import pytest

from load import get_magnitude_type_id, get_location_id, upload_data, filter_new_events


def test_get_magnitude_type_id_maps_value(mocker, test_earthquake_data):
    conn = mocker.MagicMock()
    cur = conn.cursor.return_value.__enter__.return_value
    cur.fetchall.return_value = [("md", 1), ("ml", 2),]
    result = get_magnitude_type_id(conn, test_earthquake_data)
    assert result[0]["magnitude_type_id"] == 1


def test_get_magnitude_type_id_empty_events(mocker):
    conn = mocker.MagicMock()
    cur = conn.cursor.return_value.__enter__.return_value
    cur.fetchall.return_value = []
    result = get_magnitude_type_id(conn, [])
    assert result == []


def test_get_location_id_uses_existing_country(mocker, test_earthquake_data):
    conn = mocker.MagicMock()
    cur = conn.cursor.return_value.__enter__.return_value
    cur.fetchall.return_value = [("US", 1), ("IW", 999)]
    mock_geocoder = mocker.MagicMock()
    mock_geocoder.reverse_geocode.return_value = [
        {"components": {"country_code": "US"}} 
    ]
    mocker.patch("load.OpenCageGeocode", return_value=mock_geocoder)
    mocker.patch.dict("load.ENV", {"API_KEY": "fake-key"})
    result = get_location_id(conn, test_earthquake_data)
    assert result[0]["country_id"] == 1


def test_get_location_id_defaults_to_iw(mocker, test_earthquake_data):
    conn = mocker.MagicMock()
    cur = conn.cursor.return_value.__enter__.return_value
    cur.fetchall.return_value = [("UK", 1), ("IW", 999)]
    mocker.patch.dict("load.ENV", {"API_KEY": "fake-key"})
    mock_geocoder = mocker.patch("load.OpenCageGeocode")
    mock_geocoder.return_value.reverse_geocode.return_value = [
        {"components": {}}
    ]
    result = get_location_id(conn, test_earthquake_data)
    assert result[0]["country_id"] == 999


def test_upload_data_executes_and_commits(mocker, test_earthquake_data):
    conn = mocker.MagicMock()
    cur = conn.cursor.return_value.__enter__.return_value
    upload_data(conn, test_earthquake_data)
    cur.executemany.assert_called_once()
    args, kwargs = cur.executemany.call_args
    sql, data = args
    assert "INSERT INTO event" in sql
    assert data == test_earthquake_data


def test_upload_data_with_empty_events(mocker):
    conn = mocker.MagicMock()
    cur = conn.cursor.return_value.__enter__.return_value
    upload_data(conn, [])
    cur.executemany.assert_not_called()
    conn.commit.assert_not_called()


def test_upload_data_does_not_commit_on_error(mocker, test_earthquake_data):
    conn = mocker.MagicMock()
    cur = conn.cursor.return_value.__enter__.return_value
    cur.executemany.side_effect = Exception("DB error")
    with pytest.raises(Exception):
        upload_data(conn, test_earthquake_data)
    conn.commit.assert_not_called()


def test_filters_out_existing_events(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [("e2",)]
    events = [
        {"usgs_event_id": "e1"},
        {"usgs_event_id": "e2"},
        {"usgs_event_id": "e3"},
    ]
    result = filter_new_events(mock_conn, events)
    assert result == [
        {"usgs_event_id": "e1"},
        {"usgs_event_id": "e3"},
    ]
