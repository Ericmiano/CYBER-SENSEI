# PostgreSQL Migration Guide

## Overview

This guide helps you migrate from SQLite to PostgreSQL for production use. PostgreSQL provides:
- Better concurrency and multi-user support
- ACID compliance with proper transaction handling
- Built-in backup and replication capabilities
- Superior performance for large datasets
- Enterprise-grade reliability

## Step 1: Install PostgreSQL

### On Windows
1. Download from https://www.postgresql.org/download/windows/
2. Run installer and follow wizard
3. Remember the superuser password

### On macOS
```bash
brew install postgresql@15
```

### On Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
```

### Using Docker
```yaml
# Add to docker-compose.yml
postgres:
  image: postgres:15-alpine
  environment:
    POSTGRES_USER: cyber_sensei
    POSTGRES_PASSWORD: secure_password_here
    POSTGRES_DB: cyber_sensei
  volumes:
    - postgres_data:/var/lib/postgresql/data
  ports:
    - "5432:5432"

volumes:
  postgres_data:
```

## Step 2: Create Database and User

```sql
-- Connect as superuser first
psql -U postgres

-- Create database
CREATE DATABASE cyber_sensei;

-- Create user
CREATE USER cyber_sensei_user WITH ENCRYPTED PASSWORD 'secure_password_here';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE cyber_sensei TO cyber_sensei_user;

-- Connect to new database
\c cyber_sensei

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO cyber_sensei_user;

-- Exit
\q
```

## Step 3: Update Configuration

### Update .env file
```env
# Change from:
DATABASE_URL="sqlite:///./data/cyber_sensei.db"

# To:
DATABASE_URL="postgresql://cyber_sensei_user:secure_password_here@localhost:5432/cyber_sensei"

# For Docker:
DATABASE_URL="postgresql://cyber_sensei_user:secure_password_here@postgres:5432/cyber_sensei"
```

### Update docker-compose.yml
```yaml
services:
  backend:
    depends_on:
      - postgres
    environment:
      DATABASE_URL: "postgresql://cyber_sensei_user:${POSTGRES_PASSWORD}@postgres:5432/cyber_sensei"

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: cyber_sensei_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: cyber_sensei
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

## Step 4: Install PostgreSQL Driver

```bash
pip install psycopg2-binary
# Or: pip install -r requirements.txt
```

## Step 5: Initialize Database Schema

### Option A: Using Alembic (Recommended)

```bash
# Initialize migrations (one-time)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

### Option B: Direct Schema Creation

```bash
cd backend
python -c "from app.database import create_tables; create_tables()"
```

## Step 6: Migrate Data (If Migrating from SQLite)

```bash
# Export from SQLite
sqlite3 data/cyber_sensei.db .dump > sqlite_dump.sql

# Adapt SQL syntax and import to PostgreSQL
psql -U cyber_sensei_user -d cyber_sensei < sqlite_adapted.sql
```

## Step 7: Test Connection

```python
# test_connection.py
from sqlalchemy import create_engine, text

db_url = "postgresql://cyber_sensei_user:password@localhost:5432/cyber_sensei"
engine = create_engine(db_url)

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("✓ Connection successful")
except Exception as e:
    print(f"✗ Connection failed: {e}")
```

## Step 8: Set Up Backups

### Automated Daily Backups

```bash
#!/bin/bash
# backup.sh
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/cyber_sensei"
mkdir -p $BACKUP_DIR

pg_dump -U cyber_sensei_user -h localhost cyber_sensei | gzip > $BACKUP_DIR/backup_$TIMESTAMP.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -mtime +30 -delete

echo "Backup completed: backup_$TIMESTAMP.sql.gz"
```

Schedule with cron:
```bash
0 2 * * * /path/to/backup.sh
```

### Restore from Backup

```bash
gunzip -c backup_20240101_020000.sql.gz | psql -U cyber_sensei_user -d cyber_sensei
```

## Step 9: Performance Tuning

### Connection Pooling

Use PgBouncer for connection pooling:

```ini
[databases]
cyber_sensei = host=localhost port=5432 dbname=cyber_sensei user=cyber_sensei_user password=password

[pgbouncer]
listen_port = 6432
max_client_conn = 1000
default_pool_size = 25
```

### Database Indexes

Add indexes to frequently queried columns:

```sql
CREATE INDEX idx_quiz_topic ON quiz_questions(topic_id);
CREATE INDEX idx_documents_user ON knowledge_documents(user_id);
CREATE INDEX idx_document_status ON knowledge_documents(status);
CREATE INDEX idx_interactions_user ON user_interactions(user_id);
CREATE INDEX idx_interactions_timestamp ON user_interactions(timestamp);
```

### Connection Settings

```python
# In database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    pool_pre_ping=True,
    echo=os.getenv("DB_ECHO", "false").lower() == "true"
)
```

## Troubleshooting

### Connection Refused
- Check PostgreSQL is running: `pg_isready`
- Verify credentials in DATABASE_URL
- Check firewall/network settings

### Permission Denied
- Verify user has GRANT privileges
- Check user can connect: `psql -U user -d cyber_sensei`

### Slow Queries
- Run `ANALYZE` to update statistics
- Check indexes: `SELECT * FROM pg_stat_user_indexes`
- Use EXPLAIN to analyze query plans

### Out of Connections
- Increase `max_connections` in postgresql.conf
- Use PgBouncer for connection pooling

## Monitoring

### Check Database Health

```sql
-- Database size
SELECT pg_size_pretty(pg_database_size('cyber_sensei'));

-- Table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Active connections
SELECT count(*) FROM pg_stat_activity;

-- Long-running queries
SELECT pid, now() - pg_stat_activity.query_start, query
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';
```

## References

- [PostgreSQL Official Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy PostgreSQL](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
- [PgBouncer Connection Pooling](https://www.pgbouncer.org/)
