from __future__ import annotations

import streamlit as st
from datetime import datetime, timedelta, timezone, date

UTC = timezone.utc


def timeframe_selector():
    """ Renders a timeframe selector (Last 24h / 7d / 30d / Custom) and returns (start_dt_utc, end_dt_utc, mode_str)."""

    if "tf_mode" not in st.session_state:
        st.session_state.tf_mode = "Last 7 days"
    if "tf_custom_start" not in st.session_state:
        st.session_state.tf_custom_start = (
            datetime.now(UTC) - timedelta(days=7)).date()
    if "tf_custom_end" not in st.session_state:
        st.session_state.tf_custom_end = datetime.now(UTC).date()

    left, mid, right = st.columns([1.1, 1, 1])

    left.markdown("### Date range:")

    custom_start: date = mid.date_input(
        "Start",
        key="tf_custom_start",
        label_visibility="collapsed",
    )
    custom_end: date = right.date_input(
        "End",
        key="tf_custom_end",
        label_visibility="collapsed",
    )

    b1, b2, b3, b4 = st.columns(4)

    def set_mode(mode: str):
        st.session_state.tf_mode = mode

    b1.button("Last 24 hours", use_container_width=True,
              on_click=set_mode, args=("Last 24 hours",))
    b2.button("Last 7 days", use_container_width=True,
              on_click=set_mode, args=("Last 7 days",))
    b3.button("Last 30 days", use_container_width=True,
              on_click=set_mode, args=("Last 30 days",))
    b4.button("CUSTOM", use_container_width=True,
              on_click=set_mode, args=("CUSTOM",))

    now = datetime.now(UTC)

    mode = st.session_state.tf_mode
    if mode == "Last 24 hours":
        start_dt = now - timedelta(hours=24)
        end_dt = now
    elif mode == "Last 7 days":
        start_dt = now - timedelta(days=7)
        end_dt = now
    elif mode == "Last 30 days":
        start_dt = now - timedelta(days=30)
        end_dt = now
    else:

        s = min(custom_start, custom_end)
        e = max(custom_start, custom_end)
        start_dt = datetime(s.year, s.month, s.day, 0, 0, 0, tzinfo=UTC)
        end_dt = datetime(e.year, e.month, e.day, 23, 59, 59, tzinfo=UTC)

    return start_dt, end_dt, mode
