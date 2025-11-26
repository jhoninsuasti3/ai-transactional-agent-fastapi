"""Centralized exception handlers for FastAPI."""

from datetime import datetime

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from apps.orchestrator.core.exceptions import (
    AppException,
    ExternalServiceError,
    HTTPException,
    NotFoundError,
)
from apps.orchestrator.settings import settings
from apps.orchestrator.domain.exceptions.base import DomainException

logger = structlog.get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers.

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(DomainException)
    async def domain_exception_handler(
        request: Request, exc: DomainException
    ) -> JSONResponse:
        """Handle domain exceptions."""
        logger.warning(
            "domain_exception",
            error=exc.message,
            details=exc.details,
            path=request.url.path,
        )

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": exc.message,
                "details": exc.details,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        """Handle custom HTTP exceptions."""
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
    async def not_found_handler(
        request: Request, exc: NotFoundError
    ) -> JSONResponse:
        """Handle not found errors."""
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
    async def external_service_handler(
        request: Request, exc: ExternalServiceError
    ) -> JSONResponse:
        """Handle external service errors."""
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
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        """Handle general application exceptions."""
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
    async def validation_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle request validation errors."""
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
    async def general_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle unexpected exceptions."""
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
