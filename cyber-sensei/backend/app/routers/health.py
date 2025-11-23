"""
Health and monitoring endpoints for Cyber-Sensei.
"""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import OperationalError
import redis
import logging

from ..database import SessionLocal
from ..celery_app import celery_app

router = APIRouter(tags=["monitoring"])
logger = logging.getLogger(__name__)


@router.get("/health", tags=["monitoring"])
async def health_check():
    """
    Basic health check endpoint.
    
    Returns:
        status: "healthy" if service is running
    """
    return {
        "status": "healthy",
        "service": "cyber-sensei-backend",
        "version": "2.0.0"
    }


@router.get("/health/ready", tags=["monitoring"])
async def readiness_check():
    """
    Readiness check endpoint - verifies all critical dependencies.
    
    Returns:
        Detailed status of all components
        
    Raises:
        HTTPException: If any critical component is unavailable
    """
    results = {
        "ready": True,
        "components": {}
    }
    
    # Check database connectivity
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        results["components"]["database"] = "✓ OK"
        db.close()
    except OperationalError as e:
        logger.error(f"Database check failed: {e}")
        results["components"]["database"] = "✗ FAILED"
        results["ready"] = False
    
    # Check Redis connectivity
    try:
        import os
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_client = redis.from_url(redis_url)
        redis_client.ping()
        results["components"]["redis"] = "✓ OK"
    except Exception as e:
        logger.warning(f"Redis check failed: {e}")
        results["components"]["redis"] = "✗ WARNING - Async tasks may be degraded"
    
    # Check Celery worker
    try:
        inspector = celery_app.control.inspect()
        active_workers = inspector.active()
        if active_workers:
            results["components"]["celery_workers"] = f"✓ {len(active_workers)} worker(s) active"
        else:
            results["components"]["celery_workers"] = "⚠ No active workers"
    except Exception as e:
        logger.warning(f"Celery check failed: {e}")
        results["components"]["celery_workers"] = "⚠ Cannot connect to Celery"
    
    if not results["ready"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=results
        )
    
    return results


@router.get("/health/live", tags=["monitoring"])
async def liveness_check():
    """
    Liveness check endpoint - quick response to determine if pod should stay alive.
    
    Returns:
        Simple alive status
    """
    return {"status": "alive"}
