"""Health check endpoints."""

from datetime import datetime

from fastapi import APIRouter

from apps.orchestrator.settings import settings

health_router = APIRouter()


@health_router.get("/health")
async def health_check() -> dict:
    """Basic health check endpoint.

    Returns:
        dict: Health status and application info
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
    }


@health_router.get("/health/ready")
async def readiness_check() -> dict:
    """Readiness check - checks if app is ready to serve requests.

    Returns:
        dict: Readiness status
    """
    # TODO: Add checks for database, external services, etc.
    return {
        "status": "ready",
        "checks": {
            "database": "ok",
            "external_services": "ok",
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


@health_router.get("/health/live")
async def liveness_check() -> dict:
    """Liveness check - checks if app is alive.

    Returns:
        dict: Liveness status
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }
