#!/usr/bin/env python
"""Database migration runner script."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost/cyber_sensei"
)

def check_database_connection():
    """Check if database is accessible."""
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("✓ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        return False

def get_applied_migrations(engine):
    """Get list of applied migrations."""
    inspector = inspect(engine)
    if 'alembic_version' in inspector.get_table_names():
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version_num FROM alembic_version"))
            return [row[0] for row in result]
    return []

def run_migrations():
    """Run all pending migrations."""
    try:
        from alembic.config import Config
        from alembic.script import ScriptDirectory
        from alembic.runtime.migration import MigrationContext
        from alembic.operations import Operations
        
        # Initialize Alembic configuration
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
        
        # Create engine
        engine = create_engine(DATABASE_URL, echo=False)
        
        # Check connection
        if not check_database_connection():
            return False
        
        # Get migration script directory
        script = ScriptDirectory.from_config(alembic_cfg)
        
        # Get applied migrations
        applied = get_applied_migrations(engine)
        logger.info(f"Applied migrations: {applied}")
        
        # Get all available migrations
        available = [sc.revision for sc in script.walk_revisions()]
        logger.info(f"Available migrations: {available}")
        
        # Run migrations using Alembic's upgrade command
        from alembic.command import upgrade
        upgrade(alembic_cfg, "head")
        
        logger.info("✓ All migrations applied successfully")
        return True
        
    except Exception as e:
        logger.error(f"✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_constraints_and_indexes(engine):
    """Verify that all constraints and indexes were created."""
    try:
        inspector = inspect(engine)
        
        # Check tables
        tables = inspector.get_table_names()
        logger.info(f"Tables created: {tables}")
        
        # Check indexes
        for table in tables:
            indexes = inspector.get_indexes(table)
            if indexes:
                logger.info(f"  {table}: {len(indexes)} indexes")
        
        # Check constraints
        for table in tables:
            constraints = inspector.get_unique_constraints(table)
            if constraints:
                logger.info(f"  {table}: {len(constraints)} unique constraints")
        
        logger.info("✓ Constraints and indexes verified")
        return True
        
    except Exception as e:
        logger.error(f"✗ Verification failed: {e}")
        return False

def main():
    """Main entry point."""
    logger.info("Starting database migration process...")
    
    # Create database connection
    engine = create_engine(DATABASE_URL, echo=False)
    
    # Run migrations
    if not run_migrations():
        logger.error("Migration failed!")
        sys.exit(1)
    
    # Verify
    if not verify_constraints_and_indexes(engine):
        logger.error("Verification failed!")
        sys.exit(1)
    
    logger.info("✓ Database migration completed successfully")
    sys.exit(0)

if __name__ == "__main__":
    main()
