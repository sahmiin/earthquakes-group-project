"""Testing suite for alert scripts"""
# pylint: skip-file

import json
from datetime import datetime, timezone

import pytest

from conftest import FakeCursor, FakeConn
from classes import EarthquakeEvent, Subscriber
from unittest.mock import Mock
from db_queries import (fetch_subscribers,
                        fetch_country_name,
                        fetch_recent_earthquakes)
from formatting import (format_subject,
                        format_body)
from poll_service import handle_recent_earthquakes
from preferences import matches
from sns_client import (build_filter_policy,
                        list_topic_subscriptions_map,
                        ensure_email_subscription_with_policy,
                        publish_event_once,
                        )


# Database queries tests


def test_fetch_subscribers_executes_expected_sql_and_parses_rows():
    cur = FakeCursor(
        _fetchall=[
            (1, "Alice", "alice@example.com", True, None, None),
            (2, None, "bob@example.com", False, 81, 2.5),
        ]
    )
    conn = FakeConn(cur)

    subs = fetch_subscribers(conn)

    assert len(cur.executed) == 1
    query, params = cur.executed[0]
    assert "FROM public.subscriber" in query
    assert params is None

    assert subs == [
        Subscriber(
            subscriber_id=1,
            subscriber_name="Alice",
            subscriber_email="alice@example.com",
            weekly=True,
            country_id=None,
            magnitude_value=None,
        ),
        Subscriber(
            subscriber_id=2,
            subscriber_name="",
            subscriber_email="bob@example.com",
            weekly=False,
            country_id=81,
            magnitude_value=2.5,
        ),
    ]


@pytest.mark.parametrize(
    "db_row,expected",
    [
        (("Japan",), "Japan"),
        ((None,), None),
        (None, None),
    ],
)
def test_fetch_country_name_handles_found_null_and_missing(db_row, expected):
    cur = FakeCursor(_fetchone=db_row)
    conn = FakeConn(cur)

    out = fetch_country_name(conn, country_id=81)

    assert len(cur.executed) == 1
    query, params = cur.executed[0]
    assert "FROM public.country" in query
    assert params == (81,)

    assert out == expected


def test_fetch_recent_earthquakes_hardcoded_5min_and_maps_rows():
    t = datetime(2026, 2, 6, 15, 0, 0, tzinfo=timezone.utc)

    # event_id, country_id, magnitude_value, creation_time, description, longitude, latitude
    cur = FakeCursor(
        _fetchall=[
            (100, 81, 1.2, t, "7 km W of Cobb, CA", -122.725, 38.822),
        ]
    )
    conn = FakeConn(cur)

    events = fetch_recent_earthquakes(conn)

    assert len(cur.executed) == 1
    query, params = cur.executed[0]

    # SQL assertions
    assert "FROM public.event" in query
    assert "INTERVAL '5 MINUTES'" in query.upper()
    assert params is None

    # Mapping assertions
    assert len(events) == 1
    ev = events[0]
    assert ev.earthquake_id == 100
    assert ev.country_id == 81
    assert ev.magnitude == 1.2
    assert ev.occurred_at.startswith("2026-02-06T15:00:00")
    assert "7 km W of Cobb, CA" in (ev.place or "")

# Formatting tests


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

# Poll Service Tests


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

# Preferences tests


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

# SNS_Client (Pure)


@pytest.mark.parametrize(
    "country_id,magnitude_value,expected",
    [
        (None, None, {}),
        (81, None, {"country_id": ["81"]}),
        (None, 2.0, {"magnitude": [{"numeric": [">=", 2.0]}]}),
        (81, 3.5, {"country_id": ["81"],
         "magnitude": [{"numeric": [">=", 3.5]}]}),
    ],
)
def test_build_filter_policy(country_id, magnitude_value, expected):
    assert build_filter_policy(
        country_id=country_id, magnitude_value=magnitude_value) == expected


# SNS_Client (Impure)


def test_list_topic_subscriptions_map_handles_pagination():
    sns = Mock()
    sns.list_subscriptions_by_topic.side_effect = [
        {
            "Subscriptions": [
                {"Endpoint": "a@example.com", "SubscriptionArn": "arn:sub:a"},
            ],
            "NextToken": "TOKEN",
        },
        {
            "Subscriptions": [
                {"Endpoint": "b@example.com", "SubscriptionArn": "arn:sub:b"},
            ],
        },
    ]

    m = list_topic_subscriptions_map(sns, "arn:topic")

    assert m == {"a@example.com": "arn:sub:a", "b@example.com": "arn:sub:b"}
    assert sns.list_subscriptions_by_topic.call_count == 2


def test_ensure_email_subscription_does_not_resubscribe_if_existing_confirmed():
    sns = Mock()
    existing = {"me@example.com": "arn:confirmed"}

    sub_arn = ensure_email_subscription_with_policy(
        sns,
        topic_arn="arn:topic",
        email="me@example.com",
        filter_policy={"country_id": ["81"]},
        existing_map=existing,
    )

    assert sub_arn == "arn:confirmed"
    sns.subscribe.assert_not_called()
    sns.set_subscription_attributes.assert_called_once()
    args, kwargs = sns.set_subscription_attributes.call_args
    assert kwargs["SubscriptionArn"] == "arn:confirmed"
    assert kwargs["AttributeName"] == "FilterPolicy"
    assert json.loads(kwargs["AttributeValue"]) == {"country_id": ["81"]}


def test_ensure_email_subscription_skips_policy_update_if_pending():
    sns = Mock()
    existing = {"me@example.com": "PendingConfirmation"}

    sub_arn = ensure_email_subscription_with_policy(
        sns,
        topic_arn="arn:topic",
        email="me@example.com",
        filter_policy={"magnitude": [{"numeric": [">=", 2.0]}]},
        existing_map=existing,
    )

    assert sub_arn == "PendingConfirmation"
    sns.subscribe.assert_not_called()
    sns.set_subscription_attributes.assert_not_called()


def test_ensure_email_subscription_subscribes_if_missing():
    sns = Mock()
    sns.subscribe.return_value = {"SubscriptionArn": "PendingConfirmation"}

    existing = {}
    sub_arn = ensure_email_subscription_with_policy(
        sns,
        topic_arn="arn:topic",
        email="new@example.com",
        filter_policy={},
        existing_map=existing,
    )

    assert sub_arn == "PendingConfirmation"
    sns.subscribe.assert_called_once()


def test_publish_event_once_sends_expected_message_attributes():
    sns = Mock()

    publish_event_once(
        sns,
        topic_arn="arn:topic",
        subject="Hello",
        body="Body",
        country_id=81,
        magnitude=3.2,
    )

    sns.publish.assert_called_once()
    _, kwargs = sns.publish.call_args

    assert kwargs["TopicArn"] == "arn:topic"
    assert kwargs["Subject"] == "Hello"
    assert kwargs["Message"] == "Body"
    attrs = kwargs["MessageAttributes"]
    assert attrs["country_id"]["DataType"] == "String"
    assert attrs["country_id"]["StringValue"] == "81"
    assert attrs["magnitude"]["DataType"] == "Number"
    assert attrs["magnitude"]["StringValue"].startswith("3.2")
