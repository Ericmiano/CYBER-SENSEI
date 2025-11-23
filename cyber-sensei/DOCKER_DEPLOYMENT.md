# Docker Deployment Guide

## Overview

This guide provides step-by-step instructions for building and running the Cyber-Sensei application with Docker, including all the new enhancements:
- Database-backed quiz system
- Video transcription with Celery async tasks
- Real-time chat with knowledge base integration

## Prerequisites

- Docker Desktop installed (version 29.0+)
- Docker Compose installed (version 2.0+)
- At least 8GB RAM available
- Network connectivity for image pulls from Docker Hub

## Quick Start

### Step 1: Navigate to Project Directory

```bash
cd d:\CYBER-SENSEI\cyber-sensei
```

### Step 2: Build Docker Images

```bash
# Build without cache to pick up recent Dockerfile changes
docker compose build --no-cache
```

**Expected Output:**
```
[+] Building 180.5s (45/45) FINISHED
...
Successfully built cyber-sensei-backend
Successfully built cyber-sensei-frontend
Successfully built cyber-sensei-worker
```

**Troubleshooting TLS Error:**
If you encounter: `failed to copy: local error: tls: bad record MAC`

This indicates a network/proxy configuration issue. Try:

```bash
# Option 1: Clear Docker build cache
docker system prune -a -f --volumes

# Option 2: Retry the build
docker compose build --no-cache

# Option 3: Pull base images directly first
docker pull python:3.10-slim
docker pull node:20-alpine
docker pull redis:7-alpine
docker pull ollama/ollama
```

### Step 3: Start All Services

```bash
docker compose up -d
```

**Services that will start:**
- **backend** (FastAPI on port 8000)
- **frontend** (React on port 3000)
- **redis** (Task queue broker)
- **ollama** (Local LLM)
- **worker** (Celery task worker)

### Step 4: Verify Services

```bash
# Check running containers
docker compose ps

# Expected output:
# NAME           STATUS     PORTS
# redis          Up         6379/tcp
# ollama         Up         11434/tcp  
# backend        Up         8000/tcp
# frontend       Up         3000/tcp
# worker         Up         (no ports)
```

### Step 5: Test Connectivity

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy"}

# List knowledge documents
curl http://localhost:8000/api/knowledge-base

# Get first topic quiz
curl http://localhost:8000/api/learning/topic/1/quiz
```

### Step 6: Access Applications

- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **Chat WebSocket**: ws://localhost:8000/ws/chat/{username}

---

## Testing

### Run All Tests in Docker

```bash
# Run backend tests
docker compose exec backend python -m pytest tests/ -v

# Expected output:
# 28 passed, 17 skipped in ~27s
```

### Run Specific Test Suite

```bash
# Quiz engine tests only
docker compose exec backend python -m pytest tests/test_quiz_engine.py -v

# Knowledge ingestion tests only
docker compose exec backend python -m pytest tests/test_knowledge_ingestion.py -v

# Route/integration tests (in Docker)
docker compose exec backend python -m pytest tests/test_routes.py -v
```

### Monitor Test Progress

```bash
# Run tests with live output
docker compose exec backend python -m pytest tests/ -v -s

# Run with coverage report
docker compose exec backend python -m pytest tests/ --cov=app --cov-report=html
```

---

## Usage Examples

### 1. Chat with Knowledge Base

```bash
# Connect to WebSocket
# Use a WebSocket client or curl:
curl --include \
  --no-buffer \
  --header "Connection: Upgrade" \
  --header "Upgrade: websocket" \
  --header "Sec-WebSocket-Key: SGVsbG8sIHdvcmxkIQ==" \
  --header "Sec-WebSocket-Version: 13" \
  http://localhost:8000/ws/chat/myusername

# Send a message and receive agent response
```

### 2. Upload and Ingest Video

```bash
# Upload a video file
curl -X POST "http://localhost:8000/api/knowledge-base/upload-video" \
  -F "file=@sample_video.mp4" \
  -F "username=testuser"

# Response includes document_id and status
# Status will transition: registered → pending_transcription → transcribing → processing → completed
```

### 3. Take a Quiz

```bash
# Get quiz for topic 1
curl "http://localhost:8000/api/learning/topic/1/quiz"

# Get limited practice quiz (5 questions)
curl "http://localhost:8000/api/learning/topic/1/quiz/subset?limit=5"

# Submit quiz answers
curl -X POST "http://localhost:8000/api/learning/testuser/submit-quiz" \
  -H "Content-Type: application/json" \
  -d '{
    "topic_id": 1,
    "answers": {
      "1": "B",
      "2": "A",
      "3": "C"
    }
  }'
```

### 4. Monitor Document Ingestion

```bash
# List all documents with status
curl "http://localhost:8000/api/knowledge-base" | jq '.[] | {id, filename, status, notes}'

# Get status for specific document
curl "http://localhost:8000/api/knowledge-base" | jq '.[] | select(.id==1)'
```

---

## Environment Configuration

### Key Environment Variables

Create or edit `.env` file in the project root:

```env
# OpenAI API (for agent responses)
OPENAI_API_KEY="sk-proj-xxxxx"

# Database
DATABASE_URL="sqlite:///./data/cyber_sensei.db"

# Redis (task queue)
REDIS_URL="redis://redis:6379/0"
CELERY_BROKER_URL="redis://redis:6379/0"
CELERY_RESULT_BACKEND="redis://redis:6379/0"

# Knowledge Base
KNOWLEDGE_DB_DIR="/app/data/knowledge_db"
TRANSCRIPT_DIR="/app/data/transcripts"
DATA_DIR="/app/data"

# Video Transcription (Whisper)
WHISPER_MODEL="base"           # Options: tiny, base, small, medium, large
WHISPER_DEVICE="cpu"           # Options: cpu, cuda (if GPU available)

# Celery Task Queue
USE_CELERY=true                # Enable async tasks
CELERY_TASK_ALWAYS_EAGER=false # false = async, true = sync (for debugging)

# Ollama (Local LLM)
OLLAMA_BASE_URL="http://ollama:11434"
```

### Optimization Tips

**For faster video transcription:**
- If GPU available: `WHISPER_DEVICE=cuda` (10-100x faster)
- For smaller models: `WHISPER_MODEL=tiny` or `base` (faster, less accurate)
- For faster inference: Use smaller models on CPU

**For development:**
- `CELERY_TASK_ALWAYS_EAGER=true` - run tasks synchronously for easier debugging
- Keep `WHISPER_MODEL=base` - reasonable balance of speed and accuracy

---

## Monitoring and Troubleshooting

### View Container Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f worker
docker compose logs -f redis

# Follow logs from specific time
docker compose logs --since 10m -f
```

### Common Issues

#### 1. WebSocket Connection Fails
```
Error: Failed to upgrade connection
```
**Solution**: Ensure backend is running and WebSocket middleware is loaded
```bash
docker compose restart backend
docker compose logs backend | grep -i websocket
```

#### 2. Celery Worker Not Processing Tasks
```
Error: Document status stuck in "pending_transcription"
```
**Solution**: Check worker logs and ensure Redis is accessible
```bash
docker compose logs worker | grep -i error
docker compose exec redis redis-cli PING
```

#### 3. Whisper Model Download Fails
```
Error: openai-whisper is not installed
```
**Solution**: Whisper should install with requirements, but if not:
```bash
docker compose exec backend pip install openai-whisper
```

#### 4. Out of Memory During Video Transcription
```
MemoryError: Unable to allocate memory
```
**Solution**: Use smaller Whisper model or reduce concurrent transcriptions
```bash
# In .env:
WHISPER_MODEL=base      # instead of large
CELERY_CONCURRENCY=1    # process one at a time
```

### Health Checks

```bash
# API Health
curl http://localhost:8000/health

# Redis connectivity
docker compose exec redis redis-cli PING

# Ollama availability
curl http://localhost:11434/api/tags

# Database connectivity
docker compose exec backend python -c "from app.database import SessionLocal; db = SessionLocal(); print('✓ Database OK')"

# Celery worker status
docker compose exec worker celery -A app.celery_app inspect active
```

---

## Maintenance

### Backup Data

```bash
# Backup database and knowledge base
docker cp cyber-sensei-backend:/app/data ./backup_$(date +%Y%m%d_%H%M%S)
```

### Reset to Clean State

```bash
# Stop and remove containers, volumes
docker compose down -v

# Remove all data
rm -rf data/

# Rebuild and restart
docker compose build --no-cache
docker compose up -d
```

### Update Dependencies

```bash
# Rebuild to pick up new requirements.txt
docker compose build --no-cache backend worker

# Restart services
docker compose restart backend worker
```

### Clean Up Resources

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Full cleanup (be careful!)
docker system prune -a -f --volumes
```

---

## Performance Tuning

### Celery Worker Configuration

Edit `docker-compose.yml` worker service:

```yaml
worker:
  command: celery -A app.celery_app worker 
    --loglevel=info 
    --concurrency=4          # Increase for more parallelism
    --prefetch-multiplier=1  # Keep low for long tasks
    --time-limit=3600        # 1 hour max per task
```

### Redis Configuration

For production, use Redis with persistence:

```yaml
redis:
  image: redis:7-alpine
  command: redis-server --appendonly yes  # Enable AOF persistence
  volumes:
    - redis_data:/data
    - ./redis.conf:/usr/local/etc/redis/redis.conf
```

### Database Optimization

For production, consider PostgreSQL instead of SQLite:

```env
# Instead of SQLite:
DATABASE_URL="postgresql://user:password@postgres:5432/cyber_sensei"
```

---

## Deployment to Production

### Using Docker Swarm or Kubernetes

For production deployments:

1. Replace SQLite with PostgreSQL
2. Use managed Redis (AWS ElastiCache, etc.)
3. Enable authentication and TLS
4. Use Docker secrets for credentials
5. Set up monitoring (Prometheus, Grafana)
6. Enable resource limits

### Example Production Override

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    environment:
      DATABASE_URL: postgresql://user:pass@postgres:5432/cyber_sensei
      REDIS_URL: redis://managed-redis:6379/0
    resources:
      limits:
        cpus: '2'
        memory: 2G
      reservations:
        cpus: '1'
        memory: 1G

  worker:
    deploy:
      replicas: 3
    resources:
      limits:
        cpus: '2'
        memory: 2G
```

---

## Support and Debugging

### Enable Debug Logging

```bash
# In .env
LOGLEVEL=DEBUG

# Restart services
docker compose restart
```

### Run Python Shell in Container

```bash
# Access Python REPL with app context
docker compose exec backend python

# Example:
>>> from app.database import SessionLocal
>>> from app.engines.quiz import QuizEngine
>>> db = SessionLocal()
>>> engine = QuizEngine(db)
>>> engine.get_question_count(1)
3
```

### Execute Celery Tasks Directly

```bash
# List active tasks
docker compose exec worker celery -A app.celery_app inspect active

# Get task stats
docker compose exec worker celery -A app.celery_app inspect stats

# Purge pending tasks (careful!)
docker compose exec worker celery -A app.celery_app purge
```

---

## Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **Celery Documentation**: https://docs.celeryproject.io
- **Docker Documentation**: https://docs.docker.com
- **OpenAI Whisper**: https://github.com/openai/whisper
- **SQLAlchemy ORM**: https://docs.sqlalchemy.org

---

*For issues or questions, check logs and verify all services are healthy before investigating.*
