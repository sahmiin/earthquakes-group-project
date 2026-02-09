"""Testing suite for the poll_service script"""
import pytest
from unittest.mock import Mock
from classes import Subscriber, EarthquakeEvent

from poll_service import handle_recent_earthquakes


def test_handle_recent_earthquakes_publishes_each_event_and_sets_subscriptions(monkeypatch):
    subs = [
        Subscriber(1, "A", "a@example.com", False, None, None),
        Subscriber(2, "B", "b@example.com", False, 81, 2.0),
    ]
    events = [
        EarthquakeEvent(10, 81, 3.0, "2026-02-06T10:00:00Z",
                        place="X", country_name=None),
        EarthquakeEvent(11, 81, 4.0, "2026-02-06T10:01:00Z",
                        place="Y", country_name=None),
    ]

    sns = Mock()
    conn = Mock()

    monkeypatch.setattr(
        "poll_service.fetch_subscribers", lambda _conn: subs)
    monkeypatch.setattr(
        "poll_service.fetch_recent_earthquakes", lambda _conn, minutes=5: events)
    monkeypatch.setattr("poll_service.fetch_country_name",
                        lambda _conn, country_id: "Japan")
    monkeypatch.setattr(
        "poll_service.build_filter_policy", lambda c, m: {"x": "y"})
    monkeypatch.setattr(
        "poll_service.list_topic_subscriptions_map", lambda _sns, _arn: {})
    monkeypatch.setattr(
        "poll_service.ensure_email_subscription_with_policy", lambda *a, **k: "arn:confirmed")

    published = []

    def _publish(_sns, *, topic_arn, subject, body, country_id, magnitude):
        published.append((topic_arn, country_id, magnitude, subject, body))

    monkeypatch.setattr("poll_service.publish_event_once", _publish)

    result = handle_recent_earthquakes(
        conn,
        sns_client=sns,
        topic_arn="arn:topic",
        subscribe_every_time=True,
    )

    assert result["earthquakes_found"] == 2
    assert result["published_events"] == 2
    assert len(published) == 2
    assert all(p[0] == "arn:topic" for p in published)

    assert result["subscribers"] == 2
    assert result["subscribed_attempts"] == 2
