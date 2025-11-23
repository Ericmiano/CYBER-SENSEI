import asyncio
from typing import Optional

import logging
from time import perf_counter

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os

from .core.agent import setup_agent
from .routers import users, learning, knowledge_base, labs
from .database import create_tables
from .seed import seed_database

# --- App Initialization ---
logger = logging.getLogger("cyber_sensei")
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Cyber-Sensei API",
    description="API for the Cyber-Sensei AI learning platform.",
    version="2.0.0"
)

# --- CORS Middleware ---
# Allows our frontend (on different ports/hosts) to talk to the backend
frontend_origins = [
    "http://localhost:5173",      # Vite dev server
    "http://localhost:3000",      # Alternative dev port
    "http://localhost:8080",      # Another alternative
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
]

# Add Docker container names and IPs if running in Docker
if os.getenv("DOCKER_ENV"):
    frontend_origins.extend([
        "http://frontend:5173",
        "http://frontend:3000",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Routers ---
app.include_router(users.router)
app.include_router(learning.router)
app.include_router(knowledge_base.router)
app.include_router(labs.router)

# --- Startup Event ---
@app.on_event("startup")
def on_startup():
    """Creates database tables on startup."""
    try:
        create_tables()
        print("✓ Database tables initialized")
        # Seed database with initial data (safe to call multiple times)
        try:
            seed_database()
            print("✓ Database seeding completed")
        except Exception as se:
            # Log seeding errors but don't prevent app from starting
            print(f"⚠️ Database seeding warning: {se}")
    except Exception as e:
        print(f"✗ Failed to initialize database: {e}")

# --- WebSocket for Chat ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()
_agent_executor_cache = None


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
    return {"status": "healthy"}

# --- Error Handlers ---
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"},
    )