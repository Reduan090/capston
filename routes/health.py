# routes/health.py
"""
HEALTH CHECK & MONITORING ENDPOINTS
Used for monitoring dashboard and automated health checks
"""

from fastapi import APIRouter, Response
from utils.db_connection import health_check as db_health_check
from config import logger
import time

router = APIRouter(prefix="/api/health", tags=["health"])

@router.get("/")
async def health_check():
    """
    Basic health check endpoint
    Returns 200 if healthy, 503 if database unavailable
    """
    db_status = db_health_check()
    
    if db_status["status"] == "healthy":
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "database": db_status
        }
    else:
        return Response(
            content={"status": "unhealthy", "database": db_status},
            status_code=503
        )

@router.get("/detailed")
async def detailed_health():
    """
    Detailed health check with all metrics
    Useful for monitoring dashboards
    """
    db_status = db_health_check()
    
    return {
        "status": db_status["status"],
        "database": db_status,
        "timestamp": time.time(),
        "checks": {
            "database_connection": "✅" if db_status["status"] == "healthy" else "❌",
            "api_responsive": "✅",
        }
    }

@router.get("/ready")
async def readiness():
    """
    Kubernetes-style readiness probe
    Returns 200 only if all dependencies are ready
    """
    db_status = db_health_check()
    
    if db_status["status"] == "healthy":
        return {"ready": True}
    else:
        return Response(
            content={"ready": False, "reason": "Database unavailable"},
            status_code=503
        )

@router.get("/live")
async def liveness():
    """
    Kubernetes-style liveness probe
    Returns 200 if the service is alive (even if degraded)
    """
    return {"alive": True, "timestamp": time.time()}
