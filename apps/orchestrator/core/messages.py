"""Application messages.

This module centralizes all user-facing messages, error messages, and other text
constants used throughout the application for better i18n support and maintainability.
"""


class HTTPMessages:
    """HTTP error messages."""

    BAD_REQUEST = "Bad request"
    NOT_FOUND = "Not found"
    CONFLICT = "Conflict"
    INTERNAL_ERROR = "Internal server error"
    SERVICE_UNAVAILABLE = "Service temporarily unavailable"
    UNAUTHORIZED = "User is not authorized to perform this operation"


class DomainMessages:
    """Domain and business logic messages."""

    VALIDATION_ERROR = "Validation error"
    BUSINESS_RULE_VIOLATION = "Business rule was violated"


class InfrastructureMessages:
    """Infrastructure layer messages."""

    DATABASE_ERROR = "Database operation failed"
    EXTERNAL_SERVICE_ERROR = "External service is unavailable or returned an error"
    TRANSACTION_VALIDATION_ERROR = "Transaction validation failed"


class AgentMessages:
    """LangGraph agent messages."""

    EXECUTION_FAILED = "Agent execution failed"
    STATE_INVALID = "Agent state is invalid or corrupted"
    TOOL_EXECUTION_FAILED = "Tool execution failed"


class ResourceNames:
    """Resource type names."""

    CONVERSATION = "Conversation"
    TRANSACTION = "Transaction"
    USER = "User"
    SESSION = "Session"
