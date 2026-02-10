"""Subscriber page"""
import os
from pathlib import Path
import base64
import pandas as pd
import streamlit as st
from sqlalchemy import text
from data.load import get_engine, load_earthquakes

style_sheet = os.path.join(os.path.dirname(__file__),
                           "../styles.css")
with open(str(style_sheet)) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def sidebar_logo(path: str, bg="#2C353C", pad="0", radius="0px"):
    """Adds Tremorlytics logo on sidebar."""

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


def get_email():
    """Adds input box to retrieve email."""
    email = st.text_input("Email")
    return email


def get_name():
    """Adds input box to retrieve name."""
    name = st.text_input("Name")
    return name


def get_magnitude_threshold():
    """Slider to retrieve requested magnitude."""
    magnitude = st.slider(
        "Only notify me for earthquakes with magnitude ≥",
        min_value=0.0,
        max_value=10.0,
        value=5.0,
        step=0.1
    )
    return magnitude


def get_country_from_df(df):
    """Allows user to select country from selectbox."""
    countries = (
        df[["country_id", "country_name"]]
        .dropna()
        .drop_duplicates()
        .sort_values("country_name")
    )

    country_name = st.selectbox(
        "Country",
        options=["All"] + countries["country_name"].tolist()
    )

    if country_name == "All":
        return None, "All"

    country_id = int(
        countries.loc[countries["country_name"]
                      == country_name, "country_id"].iloc[0]
    )

    return country_id, country_name


def get_weekly_alert():
    """Adds check box, to get know if user wants alerts weekly or not."""
    weekly = st.checkbox("Weekly alerts", value=True)
    return weekly


def insert_subscriber(name, email, weekly, country_id, magnitude_value):
    """Inputs all retrieved data to the subscriber table"""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO subscriber
                    (subscriber_name, subscriber_email, weekly, country_id, magnitude_value)
                VALUES
                    (:name, :email, :weekly, :country_id, :mag);
            """),
            {
                "name": name,
                "email": email,
                "weekly": bool(weekly),
                "country_id": (country_id),
                "mag": float(magnitude_value),
            },
        )


st.markdown("<div class='dashboard-title'>Subscribe to receive alerts!</div>",
            unsafe_allow_html=True)

end_dt = pd.Timestamp.utcnow()
start_dt = end_dt - pd.Timedelta(days=365)
df_quakes = load_earthquakes(start_dt, end_dt)

with st.form("subscribe_form", clear_on_submit=True):
    name = get_name()
    email = get_email()
    magnitude = get_magnitude_threshold()
    weekly = get_weekly_alert()
    country_id, country_name = get_country_from_df(df_quakes)

    submitted = st.form_submit_button("Submit")

if submitted:
    name = (name or "").strip()
    email = (email or "").strip()

    if not name:
        st.error("Enter your name.")
    elif "@" not in email or "." not in email:
        st.error("Enter a valid email address.")
    else:
        try:
            insert_subscriber(
                name=name,
                email=email,
                weekly=weekly,
                country_id=country_id,
                magnitude_value=magnitude,
            )
            st.success(
                f"Subscribed!")
        except Exception as e:
            st.error("Failed to save subscription.")
            st.exception(e)
