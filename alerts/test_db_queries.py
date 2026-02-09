"""Testing suite for db_queries script"""
import pytest

from helpers_db import FakeCursor, FakeConn
from db_queries import fetch_subscribers, fetch_country_name
from classes import Subscriber


def test_fetch_subscribers_executes_expected_sql_and_parses_rows():
    cur = FakeCursor(
        _fetchall=[
            (1, "Alice", "alice@example.com", True, None, None),
            (2, None, "bob@example.com", False, 81, 2.5),
        ]
    )
    conn = FakeConn(cur)

    subs = fetch_subscribers(conn)

    assert len(cur.executed) == 1
    query, params = cur.executed[0]
    assert "FROM public.subscriber" in query
    assert params is None

    assert subs == [
        Subscriber(
            subscriber_id=1,
            subscriber_name="Alice",
            subscriber_email="alice@example.com",
            weekly=True,
            country_id=None,
            magnitude_value=None,
        ),
        Subscriber(
            subscriber_id=2,
            subscriber_name="",
            subscriber_email="bob@example.com",
            weekly=False,
            country_id=81,
            magnitude_value=2.5,
        ),
    ]


@pytest.mark.parametrize(
    "db_row,expected",
    [
        (("Japan",), "Japan"),
        ((None,), None),
        (None, None),
    ],
)
def test_fetch_country_name_handles_found_null_and_missing(db_row, expected):
    cur = FakeCursor(_fetchone=db_row)
    conn = FakeConn(cur)

    out = fetch_country_name(conn, country_id=81)

    assert len(cur.executed) == 1
    query, params = cur.executed[0]
    assert "FROM public.country" in query
    assert params == (81,)

    assert out == expected
