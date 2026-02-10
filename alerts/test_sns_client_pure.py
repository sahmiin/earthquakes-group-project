"""Testing suite for sns_client (pure functions)"""

import pytest
from sns_client import build_filter_policy


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
