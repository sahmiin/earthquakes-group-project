"""Function to render graph"""
import pandas as pd
import streamlit as st
import altair as alt


def render_magnitude_distribution(df: pd.DataFrame) -> None:
    """Renders a magnitude distribution graph."""
    st.markdown("#### Magnitude distribution")

    if df is None or df.empty:
        st.info("No data to plot.")
        return

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("magnitude_value:Q", bin=True, title="Magnitude"),
            y=alt.Y("count()", title="Number of earthquakes")
        )
    )

    st.altair_chart(chart, use_container_width=True)
