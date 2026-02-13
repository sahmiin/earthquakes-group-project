# 🌋 Earthquakes Database Set-up 🫙

To create and seed the database, you must have the following variables within your `.env`:

```
DB_USERNAME=XXXX
DB_PASSWORD=XXXX
DB_HOST=XXXX
DB_NAME=XXXX
DB_PORT=XXXX

```

Then, to start the operation, simply run:

```
sh run_db.sh
```

This will run `schema.sql`, which creates the tables in the database; then `seed.py`, which seeds the master data.

After this your database is ready for usage in the pipeline! 🌋