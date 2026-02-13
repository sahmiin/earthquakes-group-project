"""Testing suite for the alerts functions"""
# pylint: skip-file
from __future__ import annotations
from dataclasses import dataclass
import pytest

from classes import Subscriber, EarthquakeEvent


@pytest.fixture
def any_subscriber():
    return Subscriber(
        subscriber_id=1,
        subscriber_name="Alice",
        subscriber_email="alice@example.com",
        weekly=False,
        country_id=None,
        magnitude_value=None
    )


@pytest.fixture
def japan_only_subscriber():
    return Subscriber(
        subscriber_id=2,
        subscriber_name="Bob-san",
        subscriber_email="bob@example.jp",
        weekly=False,
        country_id=116,
        magnitude_value=None
    )


@pytest.fixture
def mag_only_subscriber():
    return Subscriber(
        subscriber_id=3,
        subscriber_name="Cara",
        subscriber_email="cara@example.com",
        weekly=False,
        country_id=None,
        magnitude_value=2.0
    )


@pytest.fixture
def both_constraints_subscriber():
    return Subscriber(
        subscriber_id=4,
        subscriber_name="Dan",
        subscriber_email="dan@example.com",  # hi dan
        weekly=False,
        country_id=116,
        magnitude_value=3.5
    )


@pytest.fixture
def event_japan_small():
    return EarthquakeEvent(
        earthquake_id=10,
        country_id=116,
        magnitude=1.2,
        occurred_at="2026-02-06T10:00:00Z",
        place="7 km W of Osaka, JP",
        country_name=None
    )


@pytest.fixture
def event_japan_big():
    return EarthquakeEvent(
        earthquake_id=11,
        country_id=116,
        magnitude=9.1,
        occurred_at="2011-03-11T05:46:24Z",
        place="72 km E of Oshika, JP",
        country_name="Japan"
    )


@pytest.fixture
def event_other_big():
    return EarthquakeEvent(
        earthquake_id=12,
        country_id=235,
        magnitude=9.0,
        occurred_at="2026-02-06T10:02:00Z",
        place=None,
        country_name=None
    )


@dataclass
class FakeCursor:
    description: list = None
    executed: list = None
    _fetchall: list = None
    _fetchone: any = None

    def __post_init__(self):
        self.executed = [] if self.executed is None else self.executed
        self._fetchall = [] if self._fetchall is None else self._fetchall

    def execute(self, query, params=None):
        self.executed.append((query, params))

    def fetchall(self):
        return self._fetchall

    def fetchone(self):
        return self._fetchone

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


@dataclass
class FakeConn:
    cursor_obj: FakeCursor

    def cursor(self):
        return self.cursor_obj

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False
