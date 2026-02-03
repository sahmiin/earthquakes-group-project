-- This script should seed the earthquakes database with all necessary master data

TRUNCATE TABLE country ;
TRUNCATE TABLE agency ;
TRUNCATE TABLE magnitude_type ;


INSERT INTO country (country_name) VALUES
('United States of America'),
('Canada'),
('Ukraine'),
('Japan'),
('Russia'),
('Philippines'),
('Chile'),
('South Korea'),
('North Korea'),
('Indonesia'),
('Nicaragua'),
('Papua New Guinea'),
('Panama'),
('Columbia'),
('Peru'),
('Ecuador')
;

INSERT INTO agency (agency_id, agency_name) VALUES
('tx'),
('nc')
;

INSERT INTO magnitude_type (magnitude_type_name) VALUES
('ml'),
('md'),
('mw'),
('mb'),
('mh'),
('mfa'),
('mww'),
('mwc'),
('mwb'),
('mwr'),
('mint')
;