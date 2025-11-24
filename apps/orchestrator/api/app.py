"""FastAPI application factory.

Enterprise-grade FastAPI application with proper lifecycle management,
middleware, exception handlers, and API versioning.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Temporarily commented out until we fix import paths
# from apps.orchestrator.api.exception_handlers.handlers import register_exception_handlers
from apps.orchestrator.api.health.router import health_router
# from apps.orchestrator.api.middlewares.logging import LoggingMiddleware
# from apps.orchestrator.api.middlewares.request_id import RequestIDMiddleware
from apps.orchestrator.v1.routers.router import api_v1_router
from apps.orchestrator.databases.postgres import close_db
from apps.orchestrator.settings import settings

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.

    Handles startup and shutdown events.

    Args:
        app: FastAPI application instance

    Yields:
        None: Application is running
    """
    # Startup
    logger.info(
        "application_starting",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
    )

    # Initialize resources here if needed
    # e.g., await init_db(), await cache.connect(), etc.

    yield

    # Shutdown
    logger.info("application_shutting_down")
    await close_db()
    logger.info("application_stopped")


def create_application() -> FastAPI:
    """Create and configure FastAPI application.

    Returns:
        FastAPI: Configured application instance

    Example:
        >>> app = create_application()
        >>> # Use with uvicorn
        >>> # uvicorn src.apps.api.app:app --reload
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AI-powered transactional agent for money transfers via natural language",
        lifespan=lifespan,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
    )

    # Middleware (order matters!)
    # Temporarily commented out custom middlewares
    # app.add_middleware(RequestIDMiddleware)
    # app.add_middleware(LoggingMiddleware)

    # 3. CORS - security middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 4. GZip compression - should be late to compress responses
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # 5. Trusted Host - security (only in production)
    # if settings.is_production:
    #     app.add_middleware(
    #         TrustedHostMiddleware,
    #         allowed_hosts=["*.yourdomain.com", "yourdomain.com"],
    #     )

    # Exception handlers - temporarily commented out
    # register_exception_handlers(app)

    # Routers
    app.include_router(health_router, tags=["Health"])
    app.include_router(api_v1_router, prefix=f"{settings.API_PREFIX}/v1")

    return app


# Application instance
app = create_application()


@app.get("/", tags=["Root"])
async def root() -> dict:
    """Root endpoint with API information.

    Returns:
        dict: API metadata and available endpoints
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "AI-powered transactional agent for money transfers",
        "docs_url": f"/docs" if settings.is_development else None,
        "health_url": "/health",
        "api": {
            "v1": f"{settings.API_PREFIX}/v1",
        },
    }