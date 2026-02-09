from sns_client import build_filter_policy


def test_build_filter_policy_empty_when_no_constraints():
    assert build_filter_policy(country_id=None, magnitude_value=None) == {}


def test_build_filter_policy_country_only():
    assert build_filter_policy(country_id=81, magnitude_value=None) == {
        "country_id": ["81"]
    }


def test_build_filter_policy_magnitude_only():
    assert build_filter_policy(country_id=None, magnitude_value=2.0) == {
        "magnitude": [{"numeric": [">=", 2.0]}]
    }


def test_build_filter_policy_both():
    assert build_filter_policy(country_id=81, magnitude_value=3.5) == {
        "country_id": ["81"],
        "magnitude": [{"numeric": [">=", 3.5]}],
    }
