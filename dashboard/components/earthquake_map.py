"""Earthquake map showcasing earthquakes from time period."""
import pydeck as pdk
import streamlit as st
import pandas as pd


def render_quake_map(df: pd.DataFrame) -> None:
    """Renders map with red points showcasing earthquakes based on loaded data."""
    if df is None or df.empty:
        st.info("No earthquakes found for the selected filters/time period.")
        return

    d = df.copy()

    d["start_time_str"] = pd.to_datetime(
        d["start_time"], utc=True, errors="coerce"
    ).dt.strftime("%Y-%m-%d %H:%M:%S UTC")

    d["radius"] = (d["magnitude_value"] ** 2) * 25000

    g = (140 - d["magnitude_value"] * 20).clip(lower=0, upper=255)
    d["r"] = 255
    d["g"] = g.astype(int)
    d["b"] = 0
    d["a"] = 160

    view = pdk.ViewState(
        latitude=float(d["latitude"].median()),
        longitude=float(d["longitude"].median()),
        zoom=1.4,
        pitch=0,
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=d,
        get_position="[longitude, latitude]",
        pickable=True,
        auto_highlight=True,
        get_radius="radius",
        radius_min_pixels=2,
        radius_max_pixels=60,
        get_fill_color="[r, g, b, a]",
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view,
        map_style=None,
        tooltip={
            "html": """
                <b>{description}</b><br/>
                Country: {country_name}<br/>
                Time: {start_time_str}<br/>
                Magnitude: {magnitude_value}<br/>
                Depth: {depth} m
            """
        },
    )

    st.pydeck_chart(deck, use_container_width=True)
