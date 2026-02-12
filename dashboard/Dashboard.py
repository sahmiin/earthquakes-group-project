"""Main dashboard page"""
import os
from pathlib import Path
import base64
import altair as alt
import streamlit as st
from components.filters import timeframe_selector
from components.metrics import display_metrics
from components.map_filters import apply_map_filters
from components.earthquake_map import render_quake_map
from data.load import load_earthquakes
from data.metrics_calculations import (
    total_quakes, max_magnitude, average_magnitude, deepest, shallowest, countries_affected,)


def tremor_theme():
    """Sets colour scheme for charts."""
    return {
        "config": {
            "background": "#191919",
            "view": {"fill": "#191919", "strokeOpacity": 0},
            "axis": {
                "labelColor": "#FFFFFF",
                "titleColor": "#FFFFFF",
                "gridColor": "#FFFFFF",
                "gridOpacity": 0.15,
                "domainColor": "#121B2F",
                "tickColor": "#121B2F",
            },
            "legend": {"labelColor": "#121B2F", "titleColor": "#121B2F"},
            "title": {"color": "#121B2F"},
            "mark": {"color": "#EB4511"},

        }
    }


def sidebar_logo(path: str, bg="#2C353C", pad="0", radius="0px"):
    """Positions Tremorlytics logo."""

    data = Path(path).read_bytes()
    b64 = base64.b64encode(data).decode()

    st.sidebar.markdown(
        f"""
        <div style="background:{bg}; padding:{pad}; border-radius:{radius}; text-align:center;">
            <img src="data:image/png;base64,{b64}"
                style="width:100%; height:auto; display:block; margin:0 auto;" />
        </div>
        """,
        unsafe_allow_html=True,
    )


logo_path = os.path.join(os.path.dirname(__file__),
                         "assets/tremorlytics.png")
sidebar_logo(str(logo_path))

alt.themes.register("tremor", tremor_theme)
alt.themes.enable("tremor")


st.set_page_config(page_title="Earthquake Monitor", layout="wide")

style_sheet = os.path.join(os.path.dirname(__file__),
                           "styles.css")
with open(str(style_sheet)) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


globe_path = os.path.join(
    os.path.dirname(__file__),
    "assets/tremor_logo.png"
)

with open(globe_path, "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

st.markdown(
    f"""
    <div style="
        display:flex;
        justify-content:center;
        margin:1.2rem 0 1rem 0;
    ">
        <img src="data:image/png;base64,{b64}"
             style="height:120px; width:auto;" />
    </div>
    """,
    unsafe_allow_html=True
)


start_dt, end_dt, mode = timeframe_selector()

c1, = st.columns(1)
with c1:
    st.write("**Selected mode:**", mode)


df = load_earthquakes(start_dt, end_dt)
st.session_state["df"] = df

display_metrics(
    total_quakes(df),
    max_magnitude(df),
    average_magnitude(df),
    deepest(df),
    shallowest(df),
    countries_affected(df),
)


st.subheader("Earthquake Map")

df_filtered = apply_map_filters(df)

st.write(f"Showing **{len(df_filtered):,}** earthquakes")
render_quake_map(df_filtered)
