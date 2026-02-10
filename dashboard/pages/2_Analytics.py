import streamlit as st
import pandas as pd
import os
from pathlib import Path
import base64

from components.filters import timeframe_selector
from data.load import load_earthquakes
from visuals.analytics import CHARTS

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


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
                         "../assets/tremorlytics.png")
sidebar_logo(str(logo_path))

st.set_page_config(page_title="Analytics", layout="wide")
st.markdown("<div class='dashboard-title'>Analytics</div>",
            unsafe_allow_html=True)

start_dt, end_dt, mode = timeframe_selector()
st.write("**Selected mode:**", mode)

df = load_earthquakes(start_dt, end_dt)

if df is None or df.empty:
    st.info("No data for this time range.")
    st.stop()

chart_name = st.selectbox("Choose a chart", list(CHARTS.keys()))
CHARTS[chart_name](df)
