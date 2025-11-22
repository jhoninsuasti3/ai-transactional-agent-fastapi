"""Custom exceptions for the application.

These exceptions are used throughout the domain and application layers.
"""


class AppException(Exception):
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


class DomainException(AppException):
    """Base exception for domain layer errors."""

    pass


class ValidationError(DomainException):
    """Validation error in domain models."""

    pass


class BusinessRuleViolation(DomainException):
    """Business rule was violated."""

    pass


# Infrastructure Exceptions


class InfrastructureException(AppException):
    """Base exception for infrastructure layer errors."""

    pass


class ExternalServiceError(InfrastructureException):
    """External service is unavailable or returned an error."""

    pass


class TransactionValidationError(InfrastructureException):
    """Transaction validation failed."""

    pass


class DatabaseError(InfrastructureException):
    """Database operation failed."""

    pass


# Application Exceptions


class ApplicationException(AppException):
    """Base exception for application layer errors."""

    pass


class NotFoundError(ApplicationException):
    """Requested resource was not found."""

    def __init__(self, resource: str, identifier: str | int):
        """Initialize not found error.

        Args:
            resource: Type of resource (e.g., "Conversation", "Transaction")
            identifier: Resource identifier
        """
        message = f"{resource} with id '{identifier}' not found"
        super().__init__(message, {"resource": resource, "identifier": str(identifier)})


class ConflictError(ApplicationException):
    """Operation conflicts with current state."""

    pass


class UnauthorizedError(ApplicationException):
    """User is not authorized to perform this operation."""

    pass


# Agent Exceptions


class AgentException(AppException):
    """Base exception for LangGraph agent errors."""

    pass


class AgentExecutionError(AgentException):
    """Agent execution failed."""

    pass


class AgentStateError(AgentException):
    """Agent state is invalid or corrupted."""

    pass


class ToolExecutionError(AgentException):
    """Agent tool execution failed."""

    pass


# HTTP Exceptions (for API layer)


class HTTPException(AppException):
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


class BadRequestError(HTTPException):
    """400 Bad Request."""

    def __init__(self, message: str = "Bad request", details: dict | None = None):
        """Initialize 400 error."""
        super().__init__(400, message, details)


class NotFoundHTTPError(HTTPException):
    """404 Not Found."""

    def __init__(self, message: str = "Not found", details: dict | None = None):
        """Initialize 404 error."""
        super().__init__(404, message, details)


class ConflictHTTPError(HTTPException):
    """409 Conflict."""

    def __init__(self, message: str = "Conflict", details: dict | None = None):
        """Initialize 409 error."""
        super().__init__(409, message, details)


class InternalServerError(HTTPException):
    """500 Internal Server Error."""

    def __init__(
        self,
        message: str = "Internal server error",
        details: dict | None = None,
    ):
        """Initialize 500 error."""
        super().__init__(500, message, details)


class ServiceUnavailableError(HTTPException):
    """503 Service Unavailable."""

    def __init__(
        self,
        message: str = "Service temporarily unavailable",
        details: dict | None = None,
    ):
        """Initialize 503 error."""
        super().__init__(503, message, details)