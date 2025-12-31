#!/usr/bin/env bash
set -e

echo "=== Cyber-Sensei Backend Startup ==="

# Wait for database to be ready
echo "Waiting for database connection..."
python -c "
import sys
import time
import os
from sqlalchemy import create_engine, text

db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@postgres:5432/cyber_sensei')
max_retries = 30

for i in range(max_retries):
    try:
        engine = create_engine(db_url, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        print('✓ Database connection successful.')
        sys.exit(0)
    except Exception as e:
        if i < max_retries - 1:
            print(f'Waiting for database... (attempt {i+1}/{max_retries})')
            time.sleep(2)
        else:
            print(f'✗ Could not connect to database after {max_retries} attempts: {e}')
            sys.exit(1)
"

# Run migrations
echo "Running database migrations..."
cd /app
alembic upgrade head || {
    echo "Migration failed, attempting to create initial migration..."
    alembic revision --autogenerate -m "Initial schema" || true
    alembic upgrade head || {
        echo "Warning: Migrations failed, but continuing..."
    }
}

# Create initial data (only if tables are empty)
echo "Seeding initial data..."
python -c "
from app.seed import seed_database
try:
    seed_database()
    print('✓ Database seeded successfully.')
except Exception as e:
    print(f'⚠ Seed script warning: {e}')
    print('Continuing anyway...')
" || echo "Seed script completed with warnings."

# Start the FastAPI server
echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
