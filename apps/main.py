"""FastAPI application entry point.

Main application setup with middleware, exception handlers, and routes.
"""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from apps.core.config import settings
from apps.core.exceptions import (
    AppException,
    HTTPException,
    NotFoundError,
    ExternalServiceError,
)
from apps.core.logging import setup_logging
from apps.infrastructure.persistence.database import close_db

# Setup logging
setup_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info(
        "application_starting",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
    )

    yield

    # Shutdown
    logger.info("application_shutting_down")
    await close_db()
    logger.info("application_stopped")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered transactional agent for money transfers via natural language",
    lifespan=lifespan,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle custom HTTP exceptions.

    Args:
        request: HTTP request
        exc: HTTP exception

    Returns:
        JSON response with error details
    """
    logger.error(
        "http_exception",
        status_code=exc.status_code,
        message=exc.message,
        details=exc.details,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(NotFoundError)
async def not_found_exception_handler(
    request: Request,
    exc: NotFoundError,
) -> JSONResponse:
    """Handle NotFoundError exceptions.

    Args:
        request: HTTP request
        exc: NotFoundError exception

    Returns:
        JSON response with 404 status
    """
    logger.warning(
        "resource_not_found",
        message=exc.message,
        details=exc.details,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": exc.message,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(ExternalServiceError)
async def external_service_exception_handler(
    request: Request,
    exc: ExternalServiceError,
) -> JSONResponse:
    """Handle ExternalServiceError exceptions.

    Args:
        request: HTTP request
        exc: ExternalServiceError exception

    Returns:
        JSON response with 503 status
    """
    logger.error(
        "external_service_error",
        message=exc.message,
        details=exc.details,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": "External service temporarily unavailable",
            "message": exc.message,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle general application exceptions.

    Args:
        request: HTTP request
        exc: AppException

    Returns:
        JSON response with 500 status
    """
    logger.error(
        "application_error",
        message=exc.message,
        details=exc.details,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": exc.message if settings.is_development else "An error occurred",
            "details": exc.details if settings.is_development else {},
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Handle Pydantic validation errors.

    Args:
        request: HTTP request
        exc: RequestValidationError

    Returns:
        JSON response with 422 status
    """
    logger.warning(
        "validation_error",
        errors=exc.errors(),
        path=request.url.path,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "details": exc.errors(),
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions.

    Args:
        request: HTTP request
        exc: Exception

    Returns:
        JSON response with 500 status
    """
    logger.exception(
        "unexpected_error",
        error=str(exc),
        path=request.url.path,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.is_development else "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


# Health Check Endpoint


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Health check endpoint.

    Returns:
        Health status and application info
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/", tags=["Root"])
async def root() -> dict:
    """Root endpoint with API information.

    Returns:
        API information
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "AI-powered transactional agent for money transfers",
        "docs_url": "/docs" if settings.is_development else None,
        "health_url": "/health",
    }


# Import and include routers (will be implemented in next steps)
# from apps.api.v1 import chat, conversations, transactions
# app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
# app.include_router(conversations.router, prefix="/api/v1", tags=["Conversations"])
# app.include_router(transactions.router, prefix="/api/v1", tags=["Transactions"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "apps.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.is_development,
        log_level=settings.LOG_LEVEL.lower(),
    )