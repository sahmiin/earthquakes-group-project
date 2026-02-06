"""Python script containing the formatting functions"""
from __future__ import annotations

from classes import EarthquakeEvent


def format_subject(event: EarthquakeEvent) -> str:
    """Formats the subject of the alert"""
    country = event.country_name or f"country_id={event.country_id}"
    where = f" - {event.place}" if event.place else ""
    return f"Earthquake alert: M{event.magnitude:.1f} in {country}{where}"[:100]


def format_body(event: EarthquakeEvent) -> str:
    """Formats the body of the alert"""
    country = event.country_name or f"(country_id={event.country_id})"
    place = f"\nLocation: {event.place}" if event.place else ""
    return (
        "An earthquake has been recorded.\n\n"
        f"Earthquake ID: {event.earthquake_id}\n"
        f"Time: {event.occurred_at}\n"
        f"Country: {country}\n"
        f"Magnitude: {event.magnitude}\n"
        f"{place}\n"
    )
