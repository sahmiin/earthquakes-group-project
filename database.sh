#!/usr/bin/env bash

set -e 

DB_NAME="your_db_name"
DB_USER="your_db_user"
DB_HOST="localhost"

echo "Running schema.sql..."
psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -f schema.sql

echo "Running seed.py..."
python3 seed.py

echo "Database setup complete ✅"
