"""Python script containing the logic for matching subscriber preferences"""

from __future__ import annotations

from .classes import Subscriber, EarthquakeEvent


def matches(sub: Subscriber, event: EarthquakeEvent) -> bool:
    """
   Returns a boolean based on whether or not there is a matching preference
    """
    if sub.country_id is not None and sub.country_id != event.country_id:
        return False
    if sub.magnitude_value is not None and event.magnitude < sub.magnitude_value:
        return False
    return True
