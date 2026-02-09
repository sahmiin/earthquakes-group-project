import streamlit as st
import pandas as pd

from components.filters import timeframe_selector
from data.load import load_earthquakes
from visuals.analytics import CHARTS

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.set_page_config(page_title="Analytics", layout="wide")
st.markdown("# 📈 Analytics")

start_dt, end_dt, mode = timeframe_selector()
st.write("**Selected mode:**", mode)

df = load_earthquakes(start_dt, end_dt)

if df is None or df.empty:
    st.info("No data for this time range.")
    st.stop()

chart_name = st.selectbox("Choose a chart", list(CHARTS.keys()))
CHARTS[chart_name](df)
