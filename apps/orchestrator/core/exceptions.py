"""Custom exceptions for the application.

These exceptions are used throughout the domain and application layers.
"""

from apps.orchestrator.core.constants import (
    HTTP_STATUS_BAD_REQUEST,
    HTTP_STATUS_CONFLICT,
    HTTP_STATUS_INTERNAL_ERROR,
    HTTP_STATUS_NOT_FOUND,
    HTTP_STATUS_SERVICE_UNAVAILABLE,
)
from apps.orchestrator.core.messages import HTTPMessages


class AppError(Exception):
    """Base exception for all application exceptions."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize exception.

        Args:
            message: Human-readable error message
            details: Additional context about the error
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


# Domain Exceptions


class DomainError(AppError):
    """Base exception for domain layer errors."""

    pass


class ValidationError(DomainError):
    """Validation error in domain models."""

    pass


class BusinessRuleViolationError(DomainError):
    """Business rule was violated."""

    pass


# Infrastructure Exceptions


class InfrastructureError(AppError):
    """Base exception for infrastructure layer errors."""

    pass


class ExternalServiceError(InfrastructureError):
    """External service is unavailable or returned an error."""

    pass


class TransactionValidationError(InfrastructureError):
    """Transaction validation failed."""

    pass


class DatabaseError(InfrastructureError):
    """Database operation failed."""

    pass


# Application Exceptions


class ApplicationError(AppError):
    """Base exception for application layer errors."""

    pass


class NotFoundError(ApplicationError):
    """Requested resource was not found."""

    def __init__(self, resource: str, identifier: str | int):
        """Initialize not found error.

        Args:
            resource: Type of resource (e.g., ResourceNames.CONVERSATION, ResourceNames.TRANSACTION)
            identifier: Resource identifier
        """
        message = f"{resource} with id '{identifier}' not found"
        super().__init__(message, {"resource": resource, "identifier": str(identifier)})


class ConflictError(ApplicationError):
    """Operation conflicts with current state."""

    pass


class UnauthorizedError(ApplicationError):
    """User is not authorized to perform this operation."""

    pass


# Agent Exceptions


class AgentError(AppError):
    """Base exception for LangGraph agent errors."""

    pass


class AgentExecutionError(AgentError):
    """Agent execution failed."""

    pass


class AgentStateError(AgentError):
    """Agent state is invalid or corrupted."""

    pass


class ToolExecutionError(AgentError):
    """Agent tool execution failed."""

    pass


# HTTP Exceptions (for API layer)


class HTTPError(AppError):
    """Base HTTP exception."""

    def __init__(self, status_code: int, message: str, details: dict | None = None):
        """Initialize HTTP exception.

        Args:
            status_code: HTTP status code
            message: Error message
            details: Additional error details
        """
        super().__init__(message, details)
        self.status_code = status_code


class BadRequestError(HTTPError):
    """400 Bad Request."""

    def __init__(self, message: str = HTTPMessages.BAD_REQUEST, details: dict | None = None):
        """Initialize 400 error."""
        super().__init__(HTTP_STATUS_BAD_REQUEST, message, details)


class NotFoundHTTPError(HTTPError):
    """404 Not Found."""

    def __init__(self, message: str = HTTPMessages.NOT_FOUND, details: dict | None = None):
        """Initialize 404 error."""
        super().__init__(HTTP_STATUS_NOT_FOUND, message, details)


class ConflictHTTPError(HTTPError):
    """409 Conflict."""

    def __init__(self, message: str = HTTPMessages.CONFLICT, details: dict | None = None):
        """Initialize 409 error."""
        super().__init__(HTTP_STATUS_CONFLICT, message, details)


class InternalServerError(HTTPError):
    """500 Internal Server Error."""

    def __init__(
        self,
        message: str = HTTPMessages.INTERNAL_ERROR,
        details: dict | None = None,
    ):
        """Initialize 500 error."""
        super().__init__(HTTP_STATUS_INTERNAL_ERROR, message, details)


class ServiceUnavailableError(HTTPError):
    """503 Service Unavailable."""

    def __init__(
        self,
        message: str = HTTPMessages.SERVICE_UNAVAILABLE,
        details: dict | None = None,
    ):
        """Initialize 503 error."""
        super().__init__(HTTP_STATUS_SERVICE_UNAVAILABLE, message, details)
