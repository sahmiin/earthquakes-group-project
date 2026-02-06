"""This script contains pytest fixtures to be used across all tests in this directory."""

from unittest.mock import MagicMock

import pytest
import pandas as pd

@pytest.fixture
def fake_earthquake_data():
    return pd.DataFrame(
        {
            'event_id': 1,
            'usgs_event_id': 1234567,
            'magnitude_value': 5.0,
            'depth': 200,
            'country_name': 'Bangladesh'
        }
    )


@pytest.fixture
def fake_subscribers():
    return pd.DataFrame(
        {
            'subscriber_email': 'test@example.com'
        }
    )