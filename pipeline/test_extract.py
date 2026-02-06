"""Test script with pytest for the extract script"""

# pylint:skip-file

import pytest

from extract import check_for_text, extract_data

def test_check_for_text(valid_event):
    assert check_for_text(valid_event, "time", "value") == '2026-02-05T05:34:12.000Z'

def test_return_value_type(valid_event):
    assert type(check_for_text(valid_event, "time", "value")) == str

def test_check_for_missing_text(event_missing_value):
    assert check_for_text(event_missing_value, "time", "value") is None

def test_check_for_text_default(event_missing_value):
    assert check_for_text(event_missing_value, "time", "value", default="N/A") == "N/A"

def test_extract_data_success(mock_requests_get):
    assert len(extract_data()) == 1