from classes import EarthquakeEvent
from formatting import format_subject, format_body


def test_format_subject_prefers_country_name():
    ev = EarthquakeEvent(
        earthquake_id=1,
        country_id=81,
        magnitude=3.21,
        occurred_at="2026-02-06T00:00:00Z",
        place="Near Tokyo",
        country_name="Japan",
    )
    subj = format_subject(ev)
    assert "Japan" in subj
    assert "country_id=81" not in subj
    assert "M3.2" in subj


def test_format_subject_falls_back_to_country_id():
    ev = EarthquakeEvent(
        earthquake_id=1,
        country_id=81,
        magnitude=3.21,
        occurred_at="t",
        place=None,
        country_name=None,
    )
    subj = format_subject(ev)
    assert "country_id=81" in subj


def test_format_body_includes_location_description_when_present():
    ev = EarthquakeEvent(
        earthquake_id=123,
        country_id=81,
        magnitude=4.0,
        occurred_at="2026-02-06T00:00:00Z",
        place="7 km W of Cobb, CA (38.8220, -122.7250)",
        country_name="Japan",
    )
    body = format_body(ev)
    assert "Earthquake ID: 123" in body
    assert "Time: 2026-02-06T00:00:00Z" in body
    assert "Country: Japan" in body
    assert "Magnitude: 4.0" in body
    assert "Location: 7 km W of Cobb, CA" in body


def test_format_body_omits_location_line_when_place_missing():
    ev = EarthquakeEvent(
        earthquake_id=123,
        country_id=81,
        magnitude=4.0,
        occurred_at="t",
        place=None,
        country_name=None,
    )
    body = format_body(ev)
    assert "Location:" not in body
    assert "Country: (country_id=81)" in body
