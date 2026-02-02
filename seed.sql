-- This script should seed the earthquakes database with all necessary master data

INSERT INTO country (country_name) VALUES
('United States of America'),
('Canada'),
('Ukraine'),
('Japan')
;

INSERT INTO agency (agency_id, agency_name) VALUES
('tx'),
('nc')
;

INSERT INTO magnitude_type (magnitude_type_name) VALUES
('ml'),
('md'),
('mw')
;