"""Python script containing the construction of the data classes"""
from dataclasses import dataclass

# Organising data


@dataclass(frozen=True)
class Subscriber:
    """Defines class structure for a Subscriber object"""
    subscriber_id: int
    subscriber_name: str
    subscriber_email: str
    weekly: bool
    country_id: int
    magnitude_value: float


@dataclass(frozen=True)
class EarthquakeEvent:
    """Defines class structure for an Earthquake object"""
    earthquake_id: int
    country_id: int
    magnitude: float
    occurred_at: str
    place: str = None
    country_name: str = None
