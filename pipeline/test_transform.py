"""Testing transform.py"""

import pandas as pd
from transform import build_dataframe, convert_datatypes, drop_outliers
# pylint:skip-file


def test_build_dataframe_valid_columns(test_earthquake_data):
    test_df = build_dataframe(test_earthquake_data)

    needed_columns = [
        "usgs_event_id",
        "start_time",
        "description",
        "creation_time",
        "latitude",
        "longitude",
        "depth_value",
        "depth_uncertainty",
        "used_phase_count",
        "used_station_count",
        "azimuthal_gap",
        "magnitude_value",
        "magnitude_uncertainty",
        "magnitude_type_name",
        "agency_name",
    ]

    assert set(test_df.columns) == set(needed_columns)


def test_build_dataframe_valid_df(test_earthquake_data):
    test_df = build_dataframe(test_earthquake_data).head(1)

    actual_df = pd.DataFrame(data={
        "usgs_event_id": ["75306651"],
        "start_time": ["2026-02-03T09:53:25.370Z"],
        "description": ["7 km NW of The Geysers, CA"],
        "creation_time": ["2026-02-03T09:55:00.160Z"],
        "latitude": ["38.824333190918"],
        "longitude": ["-122.80716705322"],
        "depth_value": ["2490.0000095367"],
        "depth_uncertainty": ["419.999987"],
        "used_phase_count": ["19"],
        "used_station_count": ["19"],
        "azimuthal_gap": ["36"],
        "magnitude_value": ["0.81"],
        "magnitude_uncertainty": ["0.2"],
        "magnitude_type_name": ["md"],
        "agency_name": ["NC"],
    })

    difference_df = pd.concat([test_df, actual_df]).drop_duplicates(keep=False)

    assert difference_df.empty


def test_convert_datatypes_valid():
    test_df = pd.DataFrame(data={
        "usgs_event_id": ["75306651"],
        "start_time": ["2026-02-03T09:53:25.370Z"],
        "description": ["7 km NW of The Geysers, CA"],
        "creation_time": ["2026-02-03T09:55:00.160Z"],
        "latitude": ["38.824333190918"],
        "longitude": ["-122.80716705322"],
        "depth_value": ["2490.0000095367"],
        "depth_uncertainty": ["419.999987"],
        "used_phase_count": ["19"],
        "used_station_count": ["19"],
        "azimuthal_gap": ["36"],
        "magnitude_value": ["0.81"],
        "magnitude_uncertainty": ["0.2"],
        "magnitude_type_name": ["md"],
        "agency_name": ["NC"],
    })

    converted_df = convert_datatypes(test_df)

    assert isinstance(converted_df.loc[0, "start_time"], pd.Timestamp)
    assert isinstance(converted_df.loc[0, "creation_time"], pd.Timestamp)
    assert isinstance(converted_df.loc[0, "latitude"], float)
    assert isinstance(converted_df.loc[0, "longitude"], float)
    assert isinstance(converted_df.loc[0, "depth_value"], float)
    assert isinstance(converted_df.loc[0, "depth_uncertainty"], float)
    assert isinstance(converted_df.loc[0, "magnitude_value"], float)
    assert isinstance(converted_df.loc[0, "magnitude_uncertainty"], float)
    assert str(converted_df["usgs_event_id"].dtype) == "Int64"
    assert str(converted_df["used_phase_count"].dtype) == "Int64"
    assert str(converted_df["used_station_count"].dtype) == "Int64"
    assert str(converted_df["azimuthal_gap"].dtype) == "Int64"


def test_drop_outliers_valid():
    test_df = pd.DataFrame(data={
        "magnitude_value": [-3.0, -2.0, 0.0, 5.0, 10.0, 11.0]
    })

    no_outlier_df = drop_outliers(test_df)

    expected_df = pd.DataFrame(data={
        "magnitude_value": [-2.0, 0.0, 5.0, 10.0]
    })

    difference_df = pd.concat([no_outlier_df.reset_index(drop=True),
                               expected_df]).drop_duplicates(keep=False)

    assert difference_df.empty
