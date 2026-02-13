"""Filters for earthquake map"""
import pandas as pd
import streamlit as st


def apply_map_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Filters using magnitude and country name."""
    if df is None:
        return pd.DataFrame()

    if df.empty:
        st.slider("Magnitude", 0.0, 10.0, (0.0, 10.0), step=0.1)
        st.multiselect("Country", options=[])
        return df

    mag_min = float(df["magnitude_value"].min())
    mag_max = float(df["magnitude_value"].max())

    sel_min, sel_max = st.slider(
        "Magnitude",
        min_value=mag_min,
        max_value=mag_max,
        value=(mag_min, mag_max),
        step=0.1
    )

    country_series = df["country_name"].dropna().astype(str)
    country_options = sorted(country_series.unique().tolist())

    selected_countries = st.multiselect(
        "Country",
        options=country_options,
        default=[]
    )

    filtered = df[
        (df["magnitude_value"] >= sel_min) &
        (df["magnitude_value"] <= sel_max)
    ]

    if selected_countries:
        filtered = filtered[filtered["country_name"].astype(
            str).isin(selected_countries)]

    return filtered
