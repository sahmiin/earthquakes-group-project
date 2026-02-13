import pytest
import pandas as pd

from metrics_calculations import (
    total_quakes,
    max_magnitude,
    average_magnitude,
    deepest,
    shallowest,
    countries_affected,
)


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "magnitude_value": [4.123, 5.678, 3.456],
        "depth": [10000, 5000, 20000],
        "country_id": [1, 2, 1]
    })


@pytest.fixture
def empty_df():
    return pd.DataFrame(columns=[
        "magnitude_value",
        "depth",
        "country_id"
    ])


def test_total_quakes(sample_df):
    assert total_quakes(sample_df) == 3


def test_total_quakes_empty(empty_df):
    assert total_quakes(empty_df) == 0


def test_max_magnitude(sample_df):
    assert max_magnitude(sample_df) == 5.68


def test_max_magnitude_empty(empty_df):
    assert max_magnitude(empty_df) == "—"


def test_average_magnitude(sample_df):

    assert average_magnitude(sample_df) == 4.42


def test_average_magnitude_empty(empty_df):
    assert average_magnitude(empty_df) == "—"


def test_deepest(sample_df):
    assert deepest(sample_df) == 20.0


def test_deepest_empty(empty_df):
    assert deepest(empty_df) == "—"


def test_shallowest(sample_df):
    assert shallowest(sample_df) == 5.0


def test_shallowest_empty(empty_df):
    assert shallowest(empty_df) == "—"


def test_shallowest_all_negative():
    df = pd.DataFrame({
        "depth": [-1000, -5000],
        "magnitude_value": [1, 2],
        "country_id": [1, 1]
    })

    assert shallowest(df) == "—"


def test_countries_affected(sample_df):
    assert countries_affected(sample_df) == 2


def test_countries_affected_empty(empty_df):
    assert countries_affected(empty_df) == "—"
