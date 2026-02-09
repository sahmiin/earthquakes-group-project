import pytest
from bs4 import BeautifulSoup

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


XML = """<event catalog:eventid="us7000xyzabc" publicID="quakeml:us.anss.org/eventparameters/event/us7000xyzabc">
    <description>
        <text>M 1.2 - 10km S of Exampleville, Country</text>
    </description>
    <origin>
        <time>
        <value>2026-02-05T05:34:12.000Z</value>
        </time>
        <latitude>
        <value>37.1234</value>
        </latitude>
        <longitude>
        <value>-121.5678</value>
        </longitude>
        <depth>
        <value>8.6</value>
        <uncertainty>1.0</uncertainty>
        </depth>
    </origin>
    <magnitude>
        <mag>
        <value>1.2</value>
        <uncertainty>0.3</uncertainty>
        </mag>
        <type>ml</type>
    </magnitude>
    <creationInfo>
        <agencyID>USGS</agencyID>
        <creationTime>2026-02-05T05:35:00.000Z</creationTime>
    </creationInfo>
    <quality>
        <usedPhaseCount>14</usedPhaseCount>
        <usedStationCount>12</usedStationCount>
        <azimuthalGap>180</azimuthalGap>
    </quality>
    </event>
    """ 

@pytest.fixture
def valid_event(): 
    return BeautifulSoup(XML, "lxml-xml").event

@pytest.fixture
def event_missing_value():
    xml = """
    <event>
        <time></time>
    </event>
    """
    return BeautifulSoup(xml, "lxml-xml").event


class MockResponse:
    def __init__(self, text):
        self.text = text


@pytest.fixture
def mock_requests_get(monkeypatch):
    def _mock_get(*args, **kwargs):
        return MockResponse(XML)
    monkeypatch.setattr("requests.get", _mock_get)