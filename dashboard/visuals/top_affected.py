import pandas as pd
import streamlit as st
import altair as alt


def render_top_countries(df: pd.DataFrame, top_n: int = 10) -> None:
    """Renders a top countries with earthquake chart."""
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
