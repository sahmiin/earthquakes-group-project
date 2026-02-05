import pytest

# pylint:skip-file


@pytest.fixture
def test_earthquake_data():
    return [
        {
            "usgs_event_id": "75306651",
            "start_time": "2026-02-03T09:53:25.370Z",
            "description": "7 km NW of The Geysers, CA",
            "creation_time": "2026-02-03T09:55:00.160Z",
            "latitude": "38.824333190918",
            "longitude": "-122.80716705322",
            "depth_value": "2490.0000095367",
            "depth_uncertainty": "419.999987",
            "used_phase_count": "19",
            "used_station_count": "19",
            "azimuthal_gap": "36",
            "magnitude_value": "0.81",
            "magnitude_uncertainty": "0.2",
            "magnitude_type_name": "md",
            "agency_name": "NC"
        }
    ]
