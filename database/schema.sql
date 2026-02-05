-- This file should contain all code required to create & seed database tables.

DROP DATABASE IF EXISTS earthquakes;
CREATE DATABASE earthquakes;

\c earthquakes

DROP TABLE IF EXISTS event CASCADE;
DROP TABLE IF EXISTS country CASCADE ;
DROP TABLE IF EXISTS magnitude_type CASCADE ;
DROP TABLE IF EXISTS subscriber CASCADE ;

CREATE TABLE "event"(
    "event_id" BIGINT NOT NULL,
    "usgs_event_id" BIGINT NOT NULL GENERATED ALWAYS AS IDENTITY,
    "start_time" TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    "description" TEXT NOT NULL,
    "creation_time" TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    "longitude" FLOAT(53) NOT NULL,
    "latitude" FLOAT(53) NOT NULL,
    "depth" FLOAT(53) NOT NULL,
    "depth_uncertainty" FLOAT(53) NOT NULL,
    "used_phase_count" SMALLINT NOT NULL,
    "used_station_count" SMALLINT NOT NULL,
    "azimuthal_gap" SMALLINT NOT NULL,
    "magnitude_value" FLOAT(53) NOT NULL,
    "magnitude_uncertainty" FLOAT(53) NOT NULL,
    "magnitude_type_id" SMALLINT NOT NULL,
    "country_id" BIGINT NOT NULL
);
ALTER TABLE
    "event" ADD PRIMARY KEY("event_id");
CREATE TABLE "country"(
    "country_id" SMALLINT NOT NULL,
    "country_name" VARCHAR(255) UNIQUE NOT NULL,
    "country_code" VARCHAR(255) UNIQUE NOT NULL
);
ALTER TABLE
    "country" ADD PRIMARY KEY("country_id");
CREATE TABLE "magnitude_type"(
    "magntiude_type_id" SMALLINT NOT NULL,
    "magnitude_type_name" VARCHAR(255) UNIQUE NOT NULL
);
ALTER TABLE
    "magnitude_type" ADD PRIMARY KEY("magntiude_type_id");
CREATE TABLE "subscriber"(
    "subscriber_id" BIGINT NOT NULL,
    "subscriber_name" VARCHAR(255) NOT NULL,
    "subscriber_email" TEXT NOT NULL,
    "weekly" BOOLEAN NOT NULL,
    "country_id" SMALLINT,
    "magnitude_value" FLOAT(53) NOT NULL
);
ALTER TABLE
    "subscriber" ADD PRIMARY KEY("subscriber_id");
ALTER TABLE
    "event" ADD CONSTRAINT "event_country_id_foreign" FOREIGN KEY("country_id") REFERENCES "country"("country_id");
ALTER TABLE
    "event" ADD CONSTRAINT "event_magnitude_type_id_foreign" FOREIGN KEY("magnitude_type_id") REFERENCES "magnitude_type"("magntiude_type_id");
ALTER TABLE
    "subscriber" ADD CONSTRAINT "subscriber_country_id_foreign" FOREIGN KEY("country_id") REFERENCES "country"("country_id");
--
