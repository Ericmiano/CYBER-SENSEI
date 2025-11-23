"""
Alembic migration initialization guide and helper functions.

To initialize Alembic migrations in your project:

1. Install alembic (already in requirements.txt)
2. Initialize migrations directory (run once):
   alembic init alembic
   
3. Update alembic/env.py to use your SQLAlchemy configuration
4. Create initial migration:
   alembic revision --autogenerate -m "Initial schema"
   
5. Apply migrations:
   alembic upgrade head
   
For more information: https://alembic.sqlalchemy.org
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


def get_migration_status():
    """Get current migration status information."""
    db_url = os.getenv("DATABASE_URL", "sqlite:///./data/cyber_sensei.db")
    
    info = {
        "database_url": db_url,
        "database_type": "PostgreSQL" if "postgresql" in db_url else "SQLite",
        "migrations_enabled": os.path.exists("alembic"),
        "instructions": {
            "initialize": "alembic init alembic",
            "create_migration": "alembic revision --autogenerate -m 'Description'",
            "apply_migrations": "alembic upgrade head",
            "rollback": "alembic downgrade -1",
            "current_version": "alembic current"
        }
    }
    
    return info


def ensure_migrations_available():
    """
    Ensure Alembic migrations are properly set up.
    
    This should be called during application startup to ensure
    database schema is up to date.
    """
    if not os.path.exists("alembic"):
        logger.warning(
            "Alembic migrations directory not found. "
            "Database schema changes may not be versioned. "
            "Run: alembic init alembic"
        )
        return False
    
    return True
