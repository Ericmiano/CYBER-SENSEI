# CYBER-SENSEI - AI-Powered Cybersecurity Learning Platform

> Intelligent learning system for cybersecurity education using AI-powered personalized learning paths, knowledge ingestion, and interactive labs.

NOTE: Docker and Docker Compose files were removed from this repository to support local development without container tooling. Use the local development instructions below to run backend and frontend directly on your machine.

## Quick Local Development

Backend:

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=$(pwd)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
# Opens on http://localhost:5173
```

Or use the helper script `run_local.sh` at the repository root to start the backend.

---

## 🏗️ Architecture

```
CYBER-SENSEI/
├── backend/                      FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── models/              Database ORM models (12 total)
│   │   │   ├── user.py
│   │   │   ├── knowledge.py
│   │   │   ├── content.py
│   │   │   ├── progress.py
│   │   │   ├── quiz.py
│   │   │   ├── annotation.py
│   │   │   ├── activity.py
│   │   │   └── ...
│   │   ├── routers/              API endpoints (8 routers, 80 routes)
│   │   │   ├── users.py          User management, auth
│   │   │   ├── learning.py       Learning paths & progress
│   │   │   ├── knowledge_base.py Knowledge management
│   │   │   ├── labs.py           Lab exercises
│   │   │   ├── health.py         Health checks & monitoring
│   │   │   ├── entities.py       CRUD for all entities
│   │   │   ├── search.py         Full-text search
│   │   │   └── annotations.py    Bookmarks & annotations
│   │   ├── schemas/              Pydantic request/response models
│   │   ├── engines/              Business logic layers
│   │   │   ├── curriculum.py    Learning path generation
│   │   │   ├── knowledge_base.py Document ingestion
│   │   │   ├── lab.py            Lab validation
│   │   │   ├── progress.py       Progress tracking (BKT)
│   │   │   └── quiz.py           Quiz logic
│   │   ├── core/                 AI & agent system
│   │   │   ├── agent.py         LangChain agent setup
│   │   │   └── tools.py          Tool definitions for agent
│   │   ├── services/
│   │   │   └── knowledge_ingestion.py  Document processing
│   │   ├── database.py           SQLAlchemy setup, table creation
│   │   ├── seed.py               Initial data seeding
│   │   ├── main.py               FastAPI app, routes, startup
│   │   ├── celery_app.py         Celery configuration
│   │   ├── logging_config.py     Logging setup
│   │   ├── ml_model.py           ML recommendation engine
│   │   ├── security.py           Auth utilities
│   │   └── retry_logic.py        Circuit breaker, retry policies
│   ├── requirements.txt          Python dependencies
│   ├── Dockerfile               Backend container
│   ├── conftest.py              Pytest configuration
│   └── tests/
│       └── test_routes.py        Route integration tests
│
├── frontend/                     React 19 + Vite + Material-UI
│   ├── src/
│   │   ├── pages/              React pages
│   │   │   ├── DashboardPage.jsx    Main dashboard
│   │   │   ├── ChatPage.jsx         Chat interface
│   │   │   ├── KnowledgeBasePage.jsx Knowledge management
│   │   │   ├── CyberRangePage.jsx   Lab exercises
│   │   │   └── LabPage.jsx          Lab wrapper
│   │   ├── components/         Reusable components
│   │   │   └── ErrorBoundary.jsx  Error handling
│   │   ├── services/
│   │   │   └── api.js          Axios HTTP client
│   │   ├── App.jsx             Main routing component
│   │   ├── main.jsx            React entry point
│   │   └── index.css           Global styles
│   ├── public/                 Static assets
│   ├── package.json            NPM dependencies
│   ├── vite.config.js         Vite build config
│   ├── vitest.config.js       Vitest testing config
│   ├── Dockerfile             Frontend container (Nginx)
│   └── src/__tests__/
│       ├── api.test.js        API service tests
│       ├── App.test.jsx       App component tests
│       └── ErrorBoundary.test.jsx  Error boundary tests
│
├── shared/                      Shared utilities
├── data/                        Data storage
│   └── knowledge_db/           ChromaDB vector database
│
├── docker-compose.yml          Dev environment (9 services)
├── docker-compose.prod.yml    Production environment
├── deploy.bat / deploy.sh      Deployment scripts
├── quickstart.bat / quickstart.sh  Quick setup scripts
└── README.md                   This file
```

### Technology Stack

**Backend:**
- **FastAPI** (0.x) - Modern async web framework with automatic API docs
- **SQLAlchemy** (2.x) - ORM for database operations
- **PostgreSQL** - Primary database (SQLite fallback for testing)
- **Redis** (7-alpine) - Caching, task queue broker
- **Celery** - Async task processing (transcription, recommendations, indexing)
- **Elasticsearch** (8.5.0) - Full-text search, log aggregation
- **Ollama** - Local LLM inference (llama3, mistral, etc.)
- **LangChain** - LLM orchestration, agent framework
- **TensorFlow** - ML recommendation engine
- **Whisper** - Speech-to-text transcription

**Frontend:**
- **React** (19.1.1) - UI framework with hooks
- **Vite** (5.x) - Modern build tool with HMR
- **Material-UI** (7.3.5) - Component library
- **Axios** - HTTP client with interceptors
- **Vitest** (3.0.0) - Testing framework (JavaScript native)
- **@testing-library/react** (16.2.0) - React component testing utilities
- **jsdom** - DOM simulation for tests

**Infrastructure:**
- **Docker & Docker Compose** - Containerization & orchestration
- **Nginx** - Frontend reverse proxy
- **ChromaDB** - Vector database for embeddings (SQLite backend)
- **GitHub Actions** - CI/CD pipeline

---

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (recommended): https://www.docker.com/products/docker-desktop
- **OR** Python 3.11+ and Node.js 18+ (for local development)
- 4GB+ free disk space
- 4GB+ available RAM

### Option 1: Docker Compose (Recommended)

**Windows (Command Prompt):**
```cmd
cd path\to\cyber-sensei

# Quick setup (creates directories, .env files)
quickstart.bat

# Start all 9 services
deploy.bat start

# Wait 30-60 seconds for initialization
```

**Linux/macOS (Terminal):**
```bash
cd path/to/cyber-sensei

# Quick setup
chmod +x quickstart.sh && ./quickstart.sh

# Start all services
chmod +x deploy.sh && ./deploy.sh start

# Wait 30-60 seconds for initialization
```

**Access the Application:**
- **Frontend**: http://localhost:5173 (or http://localhost in production)
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Kibana Logs**: http://localhost:5601
- **Database**: PostgreSQL on `localhost:5432` (user: `postgres`, password: `postgres`)
- **Cache**: Redis on `localhost:6379`
- **Search**: Elasticsearch on `localhost:9200`
- **LLM**: Ollama on `localhost:11434`

### Option 2: Local Development Setup

**Backend:**
```bash
cd backend

# Create virtual environment
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment (optional)
# export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/cyber_sensei
# export SKIP_ML_ENGINE=true

# Start server with hot reload
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend

# Install dependencies
npm install

# Start dev server with hot reload
npm run dev

# Runs on http://localhost:5173

# Run tests
npm test
```

---

## 📚 Key Features

### 1. **Knowledge Base System**
- Upload documents (PDF, DOCX, TXT), videos, or text content
- Automatic text extraction and Whisper speech-to-text transcription
- ChromaDB vector database for semantic search
- Elasticsearch full-text indexing
- User-defined topics and modules for organization

### 2. **Learning Paths**
- AI-generated personalized curriculum
- Adaptive difficulty based on user performance
- Module → Topic → Content → Quiz progression
- Progress tracking with Bayesian Knowledge Tracing
- Estimated time-to-mastery calculations

### 3. **Quiz Engine**
- Multiple choice, true/false, and free-text questions
- Adaptive difficulty (IRT - Item Response Theory)
- Performance-based question selection
- Real-time feedback and explanations
- Question bank with tags and difficulty levels

### 4. **Interactive Labs**
- Hands-on cybersecurity exercises
- Automated validation and scoring
- Lab templates with pre-built scenarios
- Progress tracking per lab
- Hints and step-by-step guidance

### 5. **Real-time Chat Assistant**
- WebSocket-based real-time communication
- LLM-powered responses via Ollama/LangChain
- Context-aware answers using knowledge base
- Tool integration for dynamic functionality
- Session management and conversation history

### 6. **Monitoring & Logging**
- Elasticsearch centralized logging
- Kibana dashboards for visualization
- Health check endpoints
- Performance metrics (request duration, error rates)
- Circuit breaker pattern for resilience

---

## 🔌 API Endpoints (80 Total)

### Health & Monitoring
- `GET /health` - Application health check
- `GET /health/db` - Database connectivity
- `GET /health/redis` - Redis connectivity
- `GET /health/elasticsearch` - Elasticsearch status

### User Management
- `POST /users/register` - Create new user
- `POST /users/login` - Authenticate user
- `GET /users/profile` - Get user profile
- `PUT /users/profile` - Update user profile
- `GET /users/progress` - Get learning progress

### Learning Paths
- `GET /learning/paths` - List personalized learning paths
- `GET /learning/modules` - List modules
- `GET /learning/topics/{id}` - Get topic details
- `POST /learning/complete` - Mark content as complete
- `GET /learning/recommendations` - Get AI recommendations

### Knowledge Base
- `POST /knowledge/upload` - Upload document
- `GET /knowledge/documents` - List documents
- `GET /knowledge/search` - Search knowledge base
- `DELETE /knowledge/{id}` - Remove document
- `POST /knowledge/ingest` - Trigger async ingestion

### Quizzes
- `GET /quizzes/available` - List available quizzes
- `POST /quizzes/{id}/start` - Start quiz session
- `POST /quizzes/{id}/answer` - Submit answer
- `GET /quizzes/{id}/result` - Get quiz results

### Labs
- `GET /labs/available` - List labs
- `POST /labs/{id}/start` - Start lab exercise
- `POST /labs/{id}/submit` - Submit lab solution
- `GET /labs/{id}/validation` - Check solution

### Search & Entities
- `GET /search/full-text` - Full-text search
- `GET /entities` - List all entities
- `GET /entities/{type}` - Filter by type

### WebSocket
- `WS /ws/chat/{username}` - Real-time chat with LLM

---

## 🐳 Docker Services

The `docker-compose.yml` defines 9 services:

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| **frontend** | node:18 → nginx | 5173 / 80 | React UI |
| **backend** | python:3.11 | 8000 | FastAPI server |
| **postgres** | postgres:15 | 5432 | Primary database |
| **redis** | redis:7-alpine | 6379 | Cache & queue broker |
| **elasticsearch** | elastic.co/elasticsearch:8.5.0 | 9200 | Search & logging |
| **kibana** | elastic.co/kibana:8.5.0 | 5601 | Log visualization |
| **ollama** | ollama/ollama | 11434 | Local LLM inference |
| **celery-worker** | python:3.11 | — | Async task processor |
| **celery-beat** | python:3.11 | — | Task scheduler |

**Startup Order:**
1. Redis (no dependencies)
2. Elasticsearch (no dependencies)
3. PostgreSQL (no dependencies)
4. Backend (depends on: postgres, redis, elasticsearch, ollama)
5. Frontend (independent)
6. Kibana (depends on: elasticsearch)
7. Ollama (independent, pulls llama3 on first run)
8. Celery Worker (depends on: redis, backend)
9. Celery Beat (depends on: redis, backend)

---

## 📦 Environment Variables

**Core Database:**
```env
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/cyber_sensei
REDIS_URL=redis://redis:6379/0
ELASTICSEARCH_URL=http://elasticsearch:9200
OLLAMA_BASE_URL=http://ollama:11434
```

**Celery (Async Tasks):**
```env
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
CELERY_TASK_ALWAYS_EAGER=false
USE_CELERY=true
```

**Data Directories:**
```env
DATA_DIR=/app/data
KNOWLEDGE_DB_DIR=/app/data/knowledge_db
TRANSCRIPT_DIR=/app/data/transcripts
WHISPER_MODEL=base
WHISPER_DEVICE=cpu
```

**Feature Flags:**
```env
SKIP_ML_ENGINE=false          # Skip TensorFlow recommendation engine
DOCKER_ENV=true               # Indicate running in Docker
```

**Testing:**
```env
SKIP_ML_ENGINE=true           # Disable TensorFlow during tests
DATABASE_URL=sqlite:///:memory:  # In-memory SQLite for tests
```

---

## ✅ Verification & Testing

### Backend Verification
```bash
cd backend

# Run startup verification (checks models, schemas, routes, DB)
python verify_startup.py

# Expected output:
# [OK] Verifying model imports...
# [OK] Verifying schema imports...
# [OK] Verifying router imports...
# [OK] Verifying FastAPI app creation... 80 routes
# [OK] Verifying database table creation...
# RESULTS: 5/5 checks passed
```

### Frontend Verification
```bash
cd frontend

# Check dependencies, imports, files
node verify_frontend.js

# Expected output:
# ✓ Package Dependencies: All 6 core dependencies present
# ✓ Core Files: All 10 core files present
# ✓ App.jsx Imports: All 7 required imports present
# ✓ API Client Configuration: All 5 core API functions exported
# ✓ Component Structure: All 4 component structures verified
# ✓ No Duplicate Files
# ✓ Vite Configuration Valid
# ✓ HTML Entry Point Properly Configured
```

### Running Tests
```bash
cd frontend

# Run all tests
npm test

# Expected: 12/12 tests passing (api, ErrorBoundary, App)

cd ../backend

# Run pytest on routes
pytest tests/test_routes.py -v
```

---

## 🛠️ Deployment Commands

### Windows
```cmd
# Navigate to project root
cd C:\path\to\cyber-sensei

# Start all services
deploy.bat start

# Stop all services
deploy.bat stop

# Restart all services
deploy.bat restart

# View logs
deploy.bat logs

# Check service status
deploy.bat status

# Clean up everything (remove containers & data)
deploy.bat clean
```

### Linux/macOS
```bash
cd /path/to/cyber-sensei

chmod +x deploy.sh

./deploy.sh start      # Start
./deploy.sh stop       # Stop
./deploy.sh restart    # Restart
./deploy.sh logs       # View logs
./deploy.sh status     # Status
./deploy.sh clean      # Clean
```

### Manual Docker Compose Commands
```bash
# Start in foreground (see logs)
docker-compose -f docker-compose.yml up

# Start in background
docker-compose -f docker-compose.yml up -d

# Stop all services
docker-compose -f docker-compose.yml down

# View logs
docker-compose -f docker-compose.yml logs -f

# View logs for specific service
docker-compose -f docker-compose.yml logs -f backend

# Restart a service
docker-compose -f docker-compose.yml restart backend

# Remove everything including data
docker-compose -f docker-compose.yml down -v
```

---

## 🚨 Troubleshooting

### Docker Issues

**"Docker is not installed"**
- Install Docker Desktop: https://www.docker.com/products/docker-desktop
- Verify: `docker --version`

**"Cannot connect to Docker daemon"**
- Ensure Docker Desktop is running (Windows/macOS)
- Linux: `sudo systemctl start docker`

**"Port already in use"**
```bash
# Kill process using port (e.g., 8000)
# Windows: netstat -ano | findstr :8000
# Linux/macOS: lsof -i :8000
# Then kill the PID
```

**"Image pull failures / TLS errors"**
- Check internet connection
- Verify Docker can access registries: `docker pull hello-world`
- Try: `docker system prune` and restart Docker Desktop

**Services fail to start**
```bash
# Check logs
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Common issues:
# - Database not initialized yet (wait 30 seconds)
# - Port conflicts (close other apps using ports)
# - Low disk space (clean up: docker system prune -a)
```

### Database Issues

**"Cannot connect to PostgreSQL"**
```bash
# Verify container is running
docker ps | grep postgres

# Check credentials in docker-compose.yml
# Default: postgres / postgres

# Enter container
docker exec -it <postgres_container_id> psql -U postgres
```

**"ChromaDB vector DB issues"**
- Stored in `data/knowledge_db/`
- Safe to delete to reset: `rm -rf data/knowledge_db/`
- Will recreate on next knowledge base upload

### Frontend Issues

**"Blank page / 404"**
- Clear browser cache (Ctrl+Shift+Del)
- Verify backend is running: `curl http://localhost:8000/health`
- Check browser console for errors

**"API requests failing"**
- Verify backend is accessible: `http://localhost:8000/docs`
- Check CORS settings in `backend/app/main.py`
- Frontend default: `http://localhost:5173` (Vite dev)

### Backend Issues

**"ModuleNotFoundError: No module named 'X'"**
```bash
# Rebuild backend image
docker-compose build --no-cache backend

# Or locally:
cd backend
pip install -r requirements.txt
```

**"Celery tasks not executing"**
- Verify Redis is running: `docker ps | grep redis`
- Check Redis connection: `redis-cli ping`
- Verify `USE_CELERY=true` env variable
- Check Celery worker logs: `docker-compose logs -f celery-worker`

**"Database tables not created"**
- Check backend logs: `docker-compose logs -f backend`
- Manual migration: `docker exec backend python -c "from app.database import create_tables; create_tables()"`

---

## 📖 Development Guide

### Adding a New Endpoint

1. **Create Schema** (`backend/app/schemas/your_feature.py`):

    ```python
    from pydantic import BaseModel

    class YourRequestSchema(BaseModel):
        field1: str
        field2: int

    class YourResponseSchema(BaseModel):
        id: int
        field1: str
    ```

2. **Create Model** (`backend/app/models/your_feature.py`):

    ```python
    from sqlalchemy import Column, String, Integer
    from .base import Base

    class YourModel(Base):
        __tablename__ = "your_table"
        id = Column(Integer, primary_key=True)
        field1 = Column(String)
    ```

3. **Create Router** (`backend/app/routers/your_feature.py`):

    ```python
    from fastapi import APIRouter, Depends
    from ..schemas.your_feature import YourRequestSchema, YourResponseSchema
    from ..database import get_db

    router = APIRouter(prefix="/your-feature", tags=["your-feature"])

    @router.post("/", response_model=YourResponseSchema)
    def create_item(req: YourRequestSchema, db: Session = Depends(get_db)):
        # Implementation
        return {"id": 1, "field1": req.field1}
    ```

4. **Include Router** in `backend/app/main.py`:

    ```python
    from .routers import your_feature
    app.include_router(your_feature.router)
    ```

5. **Write Tests** (`backend/tests/test_your_feature.py`):

    ```python
    def test_create_item(client):
        response = client.post("/your-feature/", json={"field1": "test", "field2": 42})
        assert response.status_code == 200
    ```

### Adding a New Frontend Component

1. **Create Component** (`frontend/src/components/YourComponent.jsx`):

    ```jsx
    export default function YourComponent({ prop1 }) {
      return <div>{prop1}</div>;
    }
    ```

2. **Add to Page**:

    ```jsx
    import YourComponent from '../components/YourComponent';

    export default function MyPage() {
      return <YourComponent prop1="value" />;
    }
    ```

3. **Add Tests** (`frontend/src/__tests__/YourComponent.test.jsx`):

    ```javascript
    import { render, screen } from '@testing-library/react';
    import YourComponent from '../components/YourComponent';

    test('renders component', () => {
      render(<YourComponent prop1="test" />);
      expect(screen.getByText('test')).toBeInTheDocument();
    });
    ```

---

## 📝 Project Statistics

- **Backend Models**: 12 total
- **API Routers**: 8 routers covering 80 endpoints
- **Frontend Pages**: 5 main pages + components
- **Database Tables**: 12 (created automatically)
- **Docker Services**: 9 (frontend, backend, postgres, redis, elasticsearch, kibana, ollama, celery-worker, celery-beat)
- **Test Coverage**: Frontend 12/12 tests passing, Backend verification 5/5 checks
- **Total Lines of Documentation**: Comprehensive guides for deployment, development, troubleshooting

---

## 📄 License

[Specify your license here]

---

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and write tests
3. Run verification: `python verify_startup.py` (backend), `node verify_frontend.js` (frontend)
4. Run tests: `npm test` (frontend), `pytest tests/` (backend)
5. Submit pull request

---

## 📞 Support

For issues:
1. Check the **Troubleshooting** section above
2. Review `docker-compose logs -f` for detailed errors
3. Verify all prerequisites are installed
4. Check GitHub Issues (if using GitHub)

---

**Last Updated:** November 25, 2025  
**Status:** ✅ Production Ready
