"""Transform script that converts to a dataframe, cleans extracted data, and converts it back to a dictionary"""
import logging
import pandas as pd
from extract import extract_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger(__name__)


def build_dataframe(records: list[dict]) -> pd.DataFrame:
    """creates dataframe from extracted values"""
    rows = []

    for r in records:
        rows.append({
            "usgs_event_id": r["usgs_event_id"],
            "start_time": r["start_time"],
            "description": r["description"],
            "creation_time": r["creation_time"],
            "latitude": r["latitude"],
            "longitude": r["longitude"],
            "depth_value": r["depth_value"],
            "depth_uncertainty": r["depth_uncertainty"],
            "used_phase_count": r["used_phase_count"],
            "used_station_count": r["used_station_count"],
            "azimuthal_gap": r["azimuthal_gap"],
            "magnitude_value": r["magnitude_value"],
            "magnitude_uncertainty": r["magnitude_uncertainty"],
            "magnitude_type_name": r["magnitude_type_name"].lower(),
            "agency_name": r["agency_name"],
        })

    return pd.DataFrame(rows)


def convert_datatypes(df: pd.DataFrame) -> pd.DataFrame:
    """convert columns to correct datatypes for the earthquake tables"""

    df["start_time"] = pd.to_datetime(
        df["start_time"], errors="coerce", utc=True)
    df["creation_time"] = pd.to_datetime(
        df["creation_time"], errors="coerce", utc=True)
    
    numeric_columns = [
        "latitude", "longitude", "depth_value", "depth_uncertainty",
        "magnitude_value", "magnitude_uncertainty"
    ]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    
    int_cols= ["used_phase_count", "used_station_count", "azimuthal_gap"]
    for col in int_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].round()
        df[col] = df[col].astype("Int64")

    return df


def drop_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """drop rows with impossible earthquake magnitudes"""
    return df[
        (df["magnitude_value"] >= -2) &
        (df["magnitude_value"] <= 10)
    ]


def transform(records: list[dict]) -> pd.DataFrame:
    logger.info("Starting transform")
    logger.info("Raw records received: %d", len(records))

    df = build_dataframe(records)
    logger.info("build dataframe complete: %d rows", len(df))

    df = convert_datatypes(df)
    logger.info("convert datatypes complete")

    df = df[df["usgs_event_id"].notna()]

    before = len(df)
    df = drop_outliers(df)
    logger.info("drop outliers complete: dropped %d rows", before - len(df))

    logger.info("Transform finished: %d rows remaining", len(df))

    return df


if __name__ == "__main__":
    records = extract_data()
    print(transform(records))
