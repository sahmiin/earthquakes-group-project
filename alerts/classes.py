"""Python script containing the construction of the data classes"""


from __future__ import annotations

from dataclasses import dataclass

# Organising data


@dataclass(frozen=True)
class Subscriber:
    subscriber_id: int
    subscriber_name: str
    subscriber_email: str
    weekly: bool
    country_id: int
    magnitude_value: float


@dataclass(frozen=True)
class EarthquakeEvent:
    earthquake_id: int
    country_id: int
    magnitude: float
    occurred_at: str
    place: str = None
    country_name: str = None
