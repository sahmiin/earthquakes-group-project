import streamlit as st
import pandas as pd
import altair as alt


def magnitude_distribution(df: pd.DataFrame) -> None:
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
    st.markdown("### Depth distribution")

    d = df.copy()
    d["depth"] = pd.to_numeric(d["depth"], errors="coerce")  # ✅

    chart = (
        alt.Chart(d.dropna(subset=["depth"]))  # ✅
        .mark_bar()
        .encode(
            x=alt.X("depth:Q", bin=alt.Bin(
                maxbins=30), title="Depth (km)"),
            y=alt.Y("count():Q", title="Number of earthquakes"),
        )
    )
    st.altair_chart(chart, use_container_width=True)


def depth_vs_magnitude(df: pd.DataFrame) -> None:
    st.markdown("### Depth vs Magnitude")

    d = df.copy()
    d["depth"] = pd.to_numeric(
        d["depth"], errors="coerce")        # ✅
    d["magnitude_value"] = pd.to_numeric(
        d["magnitude_value"], errors="coerce")  # ✅

    chart = (
        alt.Chart(d.dropna(subset=["depth", "magnitude_value"]))  # ✅
        .mark_circle(opacity=0.5)
        .encode(
            x=alt.X("magnitude_value:Q", title="Magnitude"),
            y=alt.Y("depth:Q", title="Depth (km)"),
        )
        .interactive()
    )
    st.altair_chart(chart, use_container_width=True)


CHARTS = {
    "Magnitude distribution": magnitude_distribution,
    "Depth distribution": depth_distribution,
    "Depth vs Magnitude": depth_vs_magnitude,
}
