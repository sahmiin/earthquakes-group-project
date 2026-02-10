#!/usr/bin/env bash

set -e 
source .env

echo "Running schema.sql..."
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USERNAME" -d "postgres" -p "$DB_PORT" -f schema.sql

echo "Running seed.py..."
python3 seed.py

echo "Database setup complete ✅"