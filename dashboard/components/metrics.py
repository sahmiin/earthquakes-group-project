"""Function to display key metrics"""
import streamlit as st
import pandas as pd


def display_metrics(
        total_quakes,
        max_magnitude,
        average_magnitude,
        deepest,
        shallowest,
        countries):
    """Display key metrics of earthquakes based on timeframe selected"""

    c1, c2, c3 = st.columns(3, gap="large")

    with c1:
        st.metric("Total Quakes", total_quakes, )
    with c2:
        st.metric("Max Magnitude", max_magnitude)
    with c3:
        st.metric("Average Magnitude", average_magnitude)

    st.markdown("")

    c4, c5, c6 = st.columns(3, gap="large")

    with c4:
        st.metric("Deepest (km)", f"{deepest} km")
    with c5:
        st.metric("Shallowest (km)", f"{shallowest} km")
    with c6:
        st.metric("Countries", countries)
