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
from visuals.time_graph import render_earthquakes_over_time
from visuals.distributions import render_magnitude_distribution
from visuals.top_affected import render_top_countries


def tremor_theme():
    """Sets colour scheme for charts."""
    return {
        "config": {
            "background": "#D8C2AD",
            "view": {"fill": "#D8C2AD", "strokeOpacity": 0},
            "axis": {
                "labelColor": "#121B2F",
                "titleColor": "#121B2F",
                "gridColor": "#121B2F",
                "gridOpacity": 0.15,
                "domainColor": "#121B2F",
                "tickColor": "#121B2F",
            },
            "legend": {"labelColor": "#121B2F", "titleColor": "#121B2F"},
            "title": {"color": "#121B2F"},
            "mark": {"color": "#121B2F"},

        }
    }


def sidebar_logo(path: str, bg="#121B2F", pad="0", radius="0px"):
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


# logo_path = Path(__file__).resolve().parent / "assets" / "tremorlytics.png"
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


st.markdown("<div class='dashboard-title'>Tremorlytics</div>",
            unsafe_allow_html=True)

start_dt, end_dt, mode = timeframe_selector()

c1, = st.columns(1)
with c1:
    st.write("**Selected mode:**", mode)


df = load_earthquakes(start_dt, end_dt)

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


st.markdown(
    "<h3 style='text-align: center;'>Insights</h3>",
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:
    render_earthquakes_over_time(df_filtered)

with col2:
    render_magnitude_distribution(df_filtered)

st.markdown(
    "<h3 style='text-align: center;'>Breakdown</h3>",
    unsafe_allow_html=True
)
render_top_countries(df_filtered, top_n=10)
