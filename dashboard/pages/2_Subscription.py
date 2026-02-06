import streamlit as st
from data.load import load_earthquakes
import pandas as pd


def get_email():
    email = st.text_input("Email")
    return email


def get_name():
    name = st.text_input("Name")
    return name


def get_magnitude_threshold():
    magnitude = st.slider(
        "Only notify me for earthquakes with magnitude ≥",
        min_value=0.0,
        max_value=10.0,
        value=5.0,
        step=0.1
    )
    return magnitude


def get_country_from_df(df):
    countries = (
        df[["country_id", "country_name"]]
        .dropna()
        .drop_duplicates()
        .sort_values("country_name")
    )

    country_name = st.selectbox(
        "Country",
        options=countries["country_name"].tolist()
    )

    country_id = int(
        countries.loc[countries["country_name"]
                      == country_name, "country_id"].iloc[0]
    )

    return country_id, country_name


def get_weekly_alert():
    weekly = st.checkbox("Weekly alerts", value=True)
    return weekly


st.title("Subscribe to receive alerts!")

name = get_name()
email = get_email()
magnitude = get_magnitude_threshold()
end_dt = pd.Timestamp.utcnow()
start_dt = end_dt - pd.Timedelta(days=365)
df_quakes = load_earthquakes(start_dt, end_dt)

country_id, country_name = get_country_from_df(df_quakes)

weekly = get_weekly_alert()

st.write("Weekly alerts:", weekly)

st.write("Name:", name)
st.write("Email:", email)
st.write("Magnitude threshold:", magnitude)
st.write("Selected country:", country_name)
