import pandas as pd
import streamlit as st
import altair as alt


def render_earthquakes_over_time(df: pd.DataFrame) -> None:
    """Renders an earthquake over time graph."""
    st.markdown("#### Earthquakes over time")

    if df is None or df.empty:
        st.info("No data to plot.")
        return

    d = df.copy()
    d["start_time"] = pd.to_datetime(d["start_time"], utc=True)

    daily = (
        d.set_index("start_time")
        .resample("D")
        .size()
        .reset_index(name="count")
    )

    chart = (
        alt.Chart(daily)
        .mark_line()
        .encode(
            x=alt.X(
                "start_time:T",
                title="Time of earthquake"
            ),
            y=alt.Y(
                "count:Q",
                title="Number of earthquakes"
            )
        )
    )

    st.altair_chart(chart, use_container_width=True)
