from classes import EarthquakeEvent
from preferences import matches


def test_matches_no_constraints(any_subscriber, event_other_big):
    assert matches(any_subscriber, event_other_big) is True


def test_matches_country_only_success(japan_only_subscriber, event_japan_small):
    assert matches(japan_only_subscriber, event_japan_small) is True


def test_matches_country_only_failure(japan_only_subscriber, event_other_big):
    assert matches(japan_only_subscriber, event_other_big) is False


def test_matches_magnitude_only_success(mag_only_subscriber, event_japan_big):
    assert matches(mag_only_subscriber, event_japan_big) is True


def test_matches_magnitude_only_failure_below_threshold(mag_only_subscriber, event_japan_small):
    assert matches(mag_only_subscriber, event_japan_small) is False


def test_matches_both_success(both_constraints_subscriber, event_japan_big):
    assert matches(both_constraints_subscriber, event_japan_big) is True


def test_matches_both_fails_country(both_constraints_subscriber, event_other_big):
    assert matches(both_constraints_subscriber, event_other_big) is False


def test_matches_both_fails_magnitude(both_constraints_subscriber, event_japan_small):
    assert matches(both_constraints_subscriber, event_japan_small) is False


def test_matches_magnitude_only_inclusive_boundary(mag_only_subscriber):
    ev = EarthquakeEvent(
        earthquake_id=99,
        country_id=1,
        magnitude=2.0,
        occurred_at="2026-02-06T00:00:00Z",
        place=None,
        country_name=None,
    )
    assert matches(mag_only_subscriber, ev) is True
