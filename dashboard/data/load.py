import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
load_dotenv()


def get_engine():
    """ Create a SQLAlchemy engine for the RDS database"""
    DB_HOST = os.getenv("HOST_NAME")
    DB_PORT = os.getenv("PORT", "5432")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    connection_url = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    return create_engine(connection_url)


@st.cache_data(ttl=120)
def load_earthquakes(start_dt, end_dt):
    """ Load earthquakes data between the timeframe set """
    engine = get_engine()

    query = text("""
        SELECT
        e.*,
        c.country_name
        FROM event e
        LEFT JOIN country c
        ON e.country_id = c.country_id
        WHERE e.start_time >= :start_dt
        AND e.start_time <= :end_dt
        ORDER BY e.start_time DESC;
    """)

    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={
                         "start_dt": start_dt, "end_dt": end_dt, },)

    return df
