"""Testing suite for formatting script"""

import pytest

from classes import EarthquakeEvent
from formatting import format_subject, format_body


@pytest.mark.parametrize(
    "event,expected_contains,expected_not_contains",
    [
        (
            EarthquakeEvent(
                earthquake_id=1,
                country_id=81,
                magnitude=3.21,
                occurred_at="2026-02-06T00:00:00Z",
                place="Near Tokyo",
                country_name="Japan",
            ),
            ["Japan", "M3.2"],
            ["country_id=81"],
        ),
        (
            EarthquakeEvent(
                earthquake_id=1,
                country_id=81,
                magnitude=3.21,
                occurred_at="t",
                place=None,
                country_name=None,
            ),
            ["country_id=81", "M3.2"],
            ["Japan"],
        ),
    ],
)
def test_format_subject_contains_expected_bits(event, expected_contains, expected_not_contains):
    subj = format_subject(event)
    for token in expected_contains:
        assert token in subj
    for token in expected_not_contains:
        assert token not in subj


def test_format_body_includes_location_when_present(event_japan_big):
    body = format_body(event_japan_big)

    assert f"Earthquake ID: {event_japan_big.earthquake_id}" in body
    assert f"Time: {event_japan_big.occurred_at}" in body
    assert f"Country: {event_japan_big.country_name}" in body
    assert f"Magnitude: {event_japan_big.magnitude}" in body
    assert "Location:" in body


@pytest.mark.parametrize(
    "place,country_name,expected_country_line,expect_location_line",
    [
        (None, None, "Country: (country_id=81)", False),
        ("7 km W of Cobb, CA", None, "Country: (country_id=81)", True),
        (None, "Japan", "Country: Japan", False),
        ("Near Tokyo", "Japan", "Country: Japan", True),
    ],
)
def test_format_body_country_and_location_variants(place, country_name, expected_country_line, expect_location_line):
    ev = EarthquakeEvent(
        earthquake_id=123,
        country_id=81,
        magnitude=4.0,
        occurred_at="2026-02-06T00:00:00Z",
        place=place,
        country_name=country_name,
    )

    body = format_body(ev)
    assert expected_country_line in body

    if expect_location_line:
        assert "Location:" in body
    else:
        assert "Location:" not in body
