#! /usr/bin/env bash

# Let the DB start
python -c "
import sys
import time
import psycopg2
import os

db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@postgres:5432/cyber_sensei')
# Parse basic connection params from URL for psycopg2 if needed, 
# or just rely on SQLAlchemy check in a loop.
# Here is a simple retry loop using python:

print('Waiting for database connection...')
max_retries = 30
for i in range(max_retries):
    try:
        # We can use the app's database module if available, or just try to connect
        # This is a simplified check
        import sqlalchemy
        engine = sqlalchemy.create_engine(db_url)
        conn = engine.connect()
        conn.close()
        print('Database connection successful.')
        sys.exit(0)
    except Exception as e:
        print(f'Waiting for database... {e}')
        time.sleep(1)

print('Could not connect to database.')
sys.exit(1)
"

# Run migrations
echo "Running database migrations..."
alembic upgrade head

# Create initial data
echo "Creating initial data..."
python app/seed.py
