import streamlit as st
import pandas as pd
import altair as alt


@st.cache_resource(ttl=120)
def magnitude_distribution(df: pd.DataFrame) -> None:
    """Graph showing magnitude distribution"""
    st.markdown("### Magnitude distribution")

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("magnitude_value:Q", bin=alt.Bin(
                maxbins=30), title="Magnitude"),
            y=alt.Y("count():Q", title="Number of earthquakes"),
        )
    )
    st.altair_chart(chart, use_container_width=True)


def depth_distribution(df: pd.DataFrame) -> None:
    """Graph showing depth distribution"""
    st.markdown("### Depth distribution")

    d = df.copy()
    d["depth"] = pd.to_numeric(d["depth"], errors="coerce")

    chart = (
        alt.Chart(d.dropna(subset=["depth"]))
        .mark_bar()
        .encode(
            x=alt.X("depth:Q", bin=alt.Bin(
                maxbins=30), title="Depth (km)"),
            y=alt.Y("count():Q", title="Number of earthquakes"),
        )
    )
    st.altair_chart(chart, use_container_width=True)


def depth_vs_magnitude(df: pd.DataFrame) -> None:
    """Graph showing Depth against magnitude"""
    st.markdown("### Depth vs Magnitude")

    d = df.copy()
    d["depth"] = pd.to_numeric(
        d["depth"], errors="coerce")
    d["magnitude_value"] = pd.to_numeric(
        d["magnitude_value"], errors="coerce")

    chart = (
        alt.Chart(d.dropna(subset=["depth", "magnitude_value"]))
        .mark_circle(opacity=0.5)
        .encode(
            x=alt.X("magnitude_value:Q", title="Magnitude"),
            y=alt.Y("depth:Q", title="Depth (km)"),
        )
        .interactive()
    )
    st.altair_chart(chart, use_container_width=True)


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


def render_top_countries(df: pd.DataFrame, top_n: int = 10) -> None:
    """Renders a top countries with earthquakes chart."""
    st.markdown("#### Top affected countries")

    if df is None or df.empty:
        st.info("No data to plot.")
        return

    counts = (
        df["country_name"]
        .fillna("Unknown")
        .astype(str)
        .value_counts()
        .head(top_n)
        .reset_index()
    )
    counts.columns = ["country_name", "count"]

    chart = (
        alt.Chart(counts)
        .mark_bar()
        .encode(
            y=alt.Y("country_name:N", sort="-x", title="Country"),
            x=alt.X("count:Q", title="Number of earthquakes"),
        )
    )

    st.altair_chart(chart, use_container_width=True)


CHARTS = {
    "Magnitude distribution": magnitude_distribution,
    "Depth distribution": depth_distribution,
    "Depth vs Magnitude": depth_vs_magnitude,
    "Earthquakes over time": render_earthquakes_over_time,
    "Top countries with earthquakes": render_top_countries

}
