from datetime import datetime, timezone

from helpers_db import FakeCursor, FakeConn
from earthquake_queries import fetch_recent_earthquakes


def test_fetch_recent_earthquakes_hardcoded_5min_and_maps_rows():
    t = datetime(2026, 2, 6, 15, 0, 0, tzinfo=timezone.utc)

    # event_id, country_id, magnitude_value, creation_time, description, longitude, latitude
    cur = FakeCursor(
        _fetchall=[
            (100, 81, 1.2, t, "7 km W of Cobb, CA", -122.725, 38.822),
        ]
    )
    conn = FakeConn(cur)

    events = fetch_recent_earthquakes(conn)

    assert len(cur.executed) == 1
    query, params = cur.executed[0]

    # SQL assertions
    assert "FROM public.event" in query
    assert "INTERVAL '5 MINUTES'" in query.upper()
    assert params is None

    # Mapping assertions
    assert len(events) == 1
    ev = events[0]
    assert ev.earthquake_id == 100
    assert ev.country_id == 81
    assert ev.magnitude == 1.2
    assert ev.occurred_at.startswith("2026-02-06T15:00:00")
    assert "7 km W of Cobb, CA" in (ev.place or "")
