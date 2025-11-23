"""Base domain exceptions.

Enterprise-grade exception hierarchy for domain layer.
"""

from typing import Any


class DomainException(Exception):
    """Base exception for all domain errors.

    All domain-specific exceptions should inherit from this class.
    """

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        """Initialize domain exception.

        Args:
            message: Error message
            details: Additional error details
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class EntityNotFoundError(DomainException):
    """Raised when an entity is not found."""

    def __init__(self, entity_name: str, entity_id: Any):
        """Initialize entity not found error.

        Args:
            entity_name: Name of the entity
            entity_id: ID of the entity
        """
        message = f"{entity_name} with id '{entity_id}' not found"
        details = {"entity_name": entity_name, "entity_id": entity_id}
        super().__init__(message, details)


class EntityAlreadyExistsError(DomainException):
    """Raised when trying to create an entity that already exists."""

    def __init__(self, entity_name: str, unique_field: str, value: Any):
        """Initialize entity already exists error.

        Args:
            entity_name: Name of the entity
            unique_field: Name of the unique field
            value: Value that already exists
        """
        message = f"{entity_name} with {unique_field}='{value}' already exists"
        details = {
            "entity_name": entity_name,
            "unique_field": unique_field,
            "value": value,
        }
        super().__init__(message, details)


class ValidationError(DomainException):
    """Raised when domain validation fails."""

    def __init__(self, message: str, field: str | None = None, value: Any = None):
        """Initialize validation error.

        Args:
            message: Error message
            field: Field that failed validation
            value: Invalid value
        """
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = value
        super().__init__(message, details)


class BusinessRuleViolation(DomainException):
    """Raised when a business rule is violated."""

    def __init__(self, rule: str, message: str, context: dict[str, Any] | None = None):
        """Initialize business rule violation.

        Args:
            rule: Name of the violated rule
            message: Error message
            context: Additional context about the violation
        """
        details = {"rule": rule}
        if context:
            details.update(context)
        super().__init__(message, details)


class InvalidStateTransition(DomainException):
    """Raised when an invalid state transition is attempted."""

    def __init__(self, entity: str, from_state: str, to_state: str):
        """Initialize invalid state transition error.

        Args:
            entity: Name of the entity
            from_state: Current state
            to_state: Attempted new state
        """
        message = f"Invalid transition for {entity}: {from_state} -> {to_state}"
        details = {
            "entity": entity,
            "from_state": from_state,
            "to_state": to_state,
        }
        super().__init__(message, details)