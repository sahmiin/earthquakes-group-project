import streamlit as st
from components.filters import timeframe_selector
from components.metrics import display_metrics
from data.load import load_earthquakes
from data.metrics_calculations import total_quakes, max_magnitude, average_magnitude, deepest, shallowest, countries_affected
from components.map_filters import apply_map_filters
from components.earthquake_map import render_quake_map
from visuals.time_graph import render_earthquakes_over_time
from visuals.distributions import render_magnitude_distribution
from visuals.top_affected import render_top_countries


st.set_page_config(page_title="Earthquake Monitor", layout="wide")

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("<div class='dashboard-title'>🌍 Earthquake Monitor</div>",
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
