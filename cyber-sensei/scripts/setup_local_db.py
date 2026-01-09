"""Create local SQLite tables and seed the database for local development."""
import sys
import os

# Ensure backend package is importable when running from repo root
ROOT = os.path.dirname(os.path.dirname(__file__))  # repo root/cyber-sensei
BACKEND_PATH = os.path.join(ROOT, 'backend')
if BACKEND_PATH not in sys.path:
    sys.path.insert(0, BACKEND_PATH)

from app.database import create_tables
from app.seed import seed_database

if __name__ == '__main__':
    print('Creating tables...')
    create_tables()
    print('Seeding database...')
    seed_database()
    print('Done.')
