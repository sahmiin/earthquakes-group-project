-- This file should contain all code required to create & seed database tables.

DROP DATABASE IF EXISTS earthquakes;
CREATE DATABASE earthquakes;

\c earthquakes

CREATE TABLE country (
    country_id SMALLINT PRIMARY KEY,
    country_name UNIQUE VARCHAR(255)
);

CREATE TABLE magnitude_type (
    magnitude_type_id SMALLINT PRIMARY KEY,
    magnitude_type_name VARCHAR(255) NOT NULL
);

CREATE TABLE earthquake_location (
    earthquake_location_id BIGINT PRIMARY KEY,
    longitude FLOAT NOT NULL,
    latitude FLOAT NOT NULL,
    country_id REFERENCES country(country_id)
);

CREATE TABLE agency (
    agency_id BIGINT PRIMARY KEY,
    agency_name VARCHAR(255) NOT NULL
);

CREATE TABLE earthquake_event (
    earthquake_event_id BIGINT GENERATE AS IDENTITY PRIMARY KEY,
    usgs_event_id BIGINT UNIQUE NOT NULL,
    start_time TIMESTAMP NOT NULL,
    description TEXT NOT NULL,
    creation_time TIMESTAMP NOT NULL,
    depth FLOAT NOT NULL,
    depth_uncertainty FLOAT,
    used_phase_count SMALLINT NOT NULL,
    used_station_count SMALLINT NOT NULL,
    azimuthal_gap SMALLINT NOT NULL,
    magnitude_value FLOAT NOT NULL,
    magnitude_uncertainty FLOAT,
    magnitude_type_id REFERENCES magnitude_type(magnitude_type_id),    
    location_id REFERENCES earthquake_location(earthquake_location_id),
    magnitude_id REFERENCES earthquake_magnitude(earthquake_magnitude_id),
    agency_id REFERENCES agency(agency_id)
);