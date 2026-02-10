"""Testing suite for preferences script"""

import pytest

from classes import EarthquakeEvent
from preferences import matches


@pytest.mark.parametrize(
    "subscriber_fixture,event_fixture,expected",
    [
        ("any_subscriber", "event_other_big", True),
        ("japan_only_subscriber", "event_japan_small", True),
        ("japan_only_subscriber", "event_other_big", False),
        ("mag_only_subscriber", "event_japan_big", True),
        ("mag_only_subscriber", "event_japan_small", False),
        ("both_constraints_subscriber", "event_japan_big", True),
        ("both_constraints_subscriber", "event_other_big", False),
        ("both_constraints_subscriber", "event_japan_small", False),
    ],
)
def test_matches_matrix(request, subscriber_fixture, event_fixture, expected):
    sub = request.getfixturevalue(subscriber_fixture)
    ev = request.getfixturevalue(event_fixture)
    assert matches(sub, ev) is expected


@pytest.mark.parametrize(
    "threshold,event_mag,expected",
    [
        (2.0, 2.0, True),      # inclusive
        (2.0, 1.999, False),   # just below
        (2.0, 2.001, True),    # just above
    ],
)
def test_matches_magnitude_threshold_is_inclusive(mag_only_subscriber, threshold, event_mag, expected):
    sub = mag_only_subscriber.__class__(
        subscriber_id=mag_only_subscriber.subscriber_id,
        subscriber_name=mag_only_subscriber.subscriber_name,
        subscriber_email=mag_only_subscriber.subscriber_email,
        weekly=mag_only_subscriber.weekly,
        country_id=None,
        magnitude_value=threshold,
    )

    ev = EarthquakeEvent(
        earthquake_id=999,
        country_id=81,
        magnitude=event_mag,
        occurred_at="2026-02-06T00:00:00Z",
        place=None,
        country_name=None,
    )

    assert matches(sub, ev) is expected
