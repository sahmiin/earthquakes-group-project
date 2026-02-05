import streamlit as st
from components.filters import timeframe_selector

st.set_page_config(page_title="Earthquake Monitor", layout="wide")

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("<div class='dashboard-title'>🌍 Earthquake Monitor</div>",
            unsafe_allow_html=True)

start_dt, end_dt, mode = timeframe_selector()

st.write("Selected mode:", mode)
st.write("Start (UTC):", start_dt)
st.write("End (UTC):", end_dt)
