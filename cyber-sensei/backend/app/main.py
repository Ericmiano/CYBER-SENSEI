import asyncio
import os
from typing import Optional
from datetime import datetime
import logging
from time import perf_counter

# FastAPI imports
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Compatibility shim: some httpx versions don't accept an `app=` kwarg
# while Starlette's TestClient passes it. Add a small wrapper so tests
# that call TestClient(app) continue to work without changing test code.
try:
    import httpx
    import inspect

    _orig_httpx_client_init = httpx.Client.__init__
    try:
        sig = inspect.signature(_orig_httpx_client_init)
        if 'app' not in sig.parameters:
            def _httpx_client_init_compat(self, *args, app=None, **kwargs):
                # Drop `app` kwarg if present (Starlette passes ASGI via TestClient)
                if 'app' in kwargs:
                    kwargs.pop('app', None)
                return _orig_httpx_client_init(self, *args, **kwargs)

            httpx.Client.__init__ = _httpx_client_init_compat
    except Exception:
        # If introspection fails, don't block app startup
        pass
except Exception:
    # httpx not installed in minimal test environment — skip compatibility shim
    pass

# App imports
from .logging_config import setup_logging
from .retry_logic import get_retry_metrics, get_dead_letter_queue, get_circuit_breaker
from .ml_model import RecommendationEngine
from .core.agent import setup_agent

# Try to import LogConfig and elasticsearch setup
try:
    from .log_aggregation import LogConfig, setup_elasticsearch_indices
except ImportError:
    LogConfig = None
    setup_elasticsearch_indices = lambda: None

# Connection manager for WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()
_agent_executor_cache = None

# --- Logging Setup ---
setup_logging()
logger = logging.getLogger("cyber_sensei")

# Setup Elasticsearch logging if available
try:
    es_url = os.getenv("ELASTICSEARCH_URL")
    if es_url and LogConfig:
        LogConfig.setup_logging("cyber-sensei", elasticsearch_url=es_url)
        setup_elasticsearch_indices()
except Exception as e:
    logger.warning(f"Elasticsearch not available: {e}")

app = FastAPI(
    title="Cyber-Sensei API",
    description="API for the Cyber-Sensei AI learning platform.",
    version="2.0.0"
)

# --- Rate Limiting (optional dependency) ---
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    from slowapi.middleware import SlowAPIMiddleware

    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
except Exception:
    # slowapi is optional for tests/local runs. Provide no-op fallbacks.
    class _NoopLimiter:
        def __init__(self, *args, **kwargs):
            pass

        def limit(self, *args, **kwargs):
            def _decorator(func):
                return func
            return _decorator

    Limiter = _NoopLimiter
    def _rate_limit_exceeded_handler(request, exc):
        return JSONResponse({"detail": "rate limit exceeded"}, status_code=429)
    # set limiter to None to indicate not active
    app.state.limiter = None

# Initialize ML recommendation engine (skip during testing)
if not os.getenv("SKIP_ML_ENGINE", "false").lower() == "true":
    try:
        recommendation_engine = RecommendationEngine(
            model_dir=os.getenv("ML_MODEL_DIR", "/app/models")
        )
        app.state.recommendation_engine = recommendation_engine
    except Exception as e:
        logger.error(f"Failed to init ML engine: {e}")
        app.state.recommendation_engine = None
else:
    app.state.recommendation_engine = None

# --- CORS Middleware ---
# Allows our frontend (on different ports/hosts) to talk to the backend
frontend_origins_env = os.getenv("CORS_ORIGINS", "")
if frontend_origins_env:
    frontend_origins = [origin.strip() for origin in frontend_origins_env.split(",")]
else:
    frontend_origins = [
        "http://localhost:5173",      # Vite dev server
        "http://localhost:3000",       # Production frontend
        "http://localhost:8080",       # Alternative dev port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://frontend:4173",        # Docker internal
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time"],
)

# Include API routers
from .routers import users, learning, knowledge_base, labs, health, entities, search, annotations, gamification

app.include_router(users.router)
app.include_router(learning.router)
app.include_router(knowledge_base.router)
app.include_router(labs.router)
app.include_router(health.router)
app.include_router(entities.router)
app.include_router(search.router)
app.include_router(annotations.router)
# gamification router is optional
try:
    app.include_router(gamification.router)
except Exception:
    pass

# Add Docker container names and IPs if running in Docker
def get_agent_executor():
    global _agent_executor_cache
    if _agent_executor_cache is None:
        _agent_executor_cache = setup_agent()
    return _agent_executor_cache

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = perf_counter()
    response = await call_next(request)
    duration = (perf_counter() - start_time) * 1000
    logger.info("%s %s completed in %.2fms", request.method, request.url.path, duration)
    response.headers["X-Process-Time"] = f"{duration:.2f}ms"
    return response


@app.websocket("/ws/chat/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    try:
        await manager.connect(websocket)
        print(f"WebSocket connection opened for user: {username}")
        
        try:
            agent_executor = get_agent_executor()
        except Exception as e:
            print(f"Failed to setup agent: {e}")
            await manager.send_personal_message(
                f"Error: Unable to initialize the chat agent. Details: {str(e)}", 
                websocket
            )
            manager.disconnect(websocket)
            return
        
        try:
            while True:
                data = await websocket.receive_text()
                print(f"Message from {username}: {data}")
                
                try:
                    response = await asyncio.to_thread(
                        agent_executor.invoke,
                        {"input": f"User '{username}' says: {data}"},
                    )
                    message_to_send = response.get('output', 'I encountered an error processing your request.')
                except Exception as e:
                    print(f"Agent invocation error: {e}")
                    message_to_send = f"Error processing request: {str(e)}"
                
                await manager.send_personal_message(message_to_send, websocket)
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            print(f"WebSocket connection closed for user: {username}")
        except Exception as e:
            print(f"WebSocket error for {username}: {e}")
            manager.disconnect(websocket)
    except Exception as e:
        print(f"Failed to establish WebSocket connection: {e}")


# --- Monitoring & Diagnostic Endpoints ---
@app.get("/api/monitoring/metrics")
async def get_metrics():
    """Get system metrics and retry statistics."""
    return {
        "retry_metrics": get_retry_metrics().get_stats(),
        "circuit_breaker": get_circuit_breaker().get_state(),
        "failed_tasks": len(get_dead_letter_queue().queue),
        "timestamp": str(datetime.utcnow())
    }


@app.get("/api/monitoring/dead-letter-queue")
async def get_dlq(limit: int = 100):
    """Get recent failed tasks from dead letter queue."""
    return {
        "failed_tasks": get_dead_letter_queue().get_failed_tasks(limit),
        "queue_size": len(get_dead_letter_queue().queue)
    }


@app.post("/api/recommendations/{user_id}")
async def get_recommendations(user_id: str):
    """Get personalized learning recommendations for user."""
    try:
        from .database import SessionLocal
        from .models import Topic, UserProgress, User
        
        db = SessionLocal()
        try:
            # Validate user exists
            user = db.query(User).filter(User.id == int(user_id) if user_id.isdigit() else False).first()
            if not user:
                # Try by username
                user = db.query(User).filter(User.username == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Get all available topics
            all_topics = db.query(Topic).all()
            topic_ids = [t.id for t in all_topics]
            
            # Get user's progress
            user_progress = {}
            for progress in db.query(UserProgress).filter(UserProgress.user_id == user.id).all():
                user_progress[progress.topic_id] = {
                    "completion_percentage": progress.completion_percentage or 0,
                    "quiz_score": 0,
                    "time_spent_seconds": 0,
                    "engagement_score": min((progress.completion_percentage or 0) / 100.0, 1.0)
                }
            
            # Get recommendations using ML engine if available, otherwise use simple heuristic
            recommendation_engine = app.state.recommendation_engine
            if recommendation_engine:
                recommendations = recommendation_engine.get_recommendations(
                    str(user.id), topic_ids, user_progress
                )
            else:
                # Fallback: simple heuristic-based recommendations
                # Recommend topics user hasn't started or has low completion
                started_topic_ids = set(user_progress.keys())
                unstarted_topics = [t for t in all_topics if t.id not in started_topic_ids]
                in_progress_topics = [
                    t for t in all_topics 
                    if t.id in started_topic_ids and user_progress.get(t.id, {}).get("completion_percentage", 0) < 50
                ]
                
                # Prioritize unstarted topics, then in-progress
                recommended = unstarted_topics[:5] + in_progress_topics[:3]
                recommendations = [
                    {
                        "topic_id": t.id,
                        "topic_name": t.name,
                        "reason": "Not started" if t.id not in started_topic_ids else "In progress",
                        "score": 0.8 if t.id not in started_topic_ids else 0.6
                    }
                    for t in recommended[:5]
                ]
            
            return {
                "user_id": str(user.id),
                "recommendations": recommendations,
                "timestamp": datetime.utcnow().isoformat()
            }
        finally:
            db.close()
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "detail": "Failed to generate recommendations"}
        )


# --- Root Endpoint ---
@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Cyber-Sensei API",
        "docs": "/docs",
        "version": "2.0.0"
    }

# --- Health Check ---
@app.get("/health")
def health_check():
    from datetime import datetime
    return {
        "status": "healthy",
        "service": "cyber-sensei-backend",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

# --- Error Handlers ---
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"},
    )