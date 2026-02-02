-- This file should contain all code required to create & seed database tables.



DROP DATABASE IF EXISTS earthquakes;
CREATE DATABASE earthquakes;

\c earthquakes

CREATE TABLE country (
    country_id SMALLINT PRIMARY KEY,
    country_name VARCHAR(255)
);

CREATE TABLE type (
    type_id SMALLINT PRIMARY KEY,
    type_name VARCHAR(255)
);

CREATE TABLE location (
    location_id BIGINT PRIMARY KEY,
    longitude FLOAT,
    latitude FLOAT,
    country_id REFERENCES type(country_id)
);

CREATE TABLE magnitude (
    magnitude_id SMALLINT PRIMARY KEY,
    value FLOAT,
    uncertainty FLOAT,
    type_id REFERENCES type(type_id)
);

CREATE TABLE agency (
    agency_id BIGINT PRIMARY KEY,
    agency_name VARCHAR(255)
);

CREATE TABLE event (
    event_id BIGINT PRIMARY KEY,
    start_time TIMESTAMP,
    description TEXT,
    creation_time TIMESTAMP,
    depth FLOAT,
    depth_uncertainty FLOAT,
    used_phase_count SMALLINT,
    used_station_count SMALLINT,
    azimuthal_gap SMALLINT,
    location_id BIGINT,
    magnitude_id SMALLINT,
    agency_id BIGINT,
    FOREIGN KEY location_id,
    FOREIGN KEY magnitude_id,
    FOREIGN KEY agency_id
);