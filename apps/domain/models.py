"""Domain models - Core business entities and value objects.

This module defines the pure domain layer with no framework dependencies.
Following Domain-Driven Design (DDD) principles.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class TransactionStatus(str, Enum):
    """Transaction status enumeration."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class ConversationStatus(str, Enum):
    """Conversation status enumeration."""

    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class Currency(str, Enum):
    """Currency codes."""

    COP = "COP"  # Colombian Peso
    USD = "USD"  # US Dollar
    EUR = "EUR"  # Euro


# Value Objects


class PhoneNumber(BaseModel):
    """Phone number value object with validation."""

    value: str = Field(..., description="Phone number (10 digits)")

    @field_validator("value")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format (Colombian: 10 digits)."""
        # Remove common separators
        cleaned = v.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

        # Must be exactly 10 digits
        if not cleaned.isdigit():
            raise ValueError("Phone number must contain only digits")

        if len(cleaned) != 10:
            raise ValueError("Phone number must be exactly 10 digits")

        # Colombian mobile numbers start with 3
        if not cleaned.startswith("3"):
            raise ValueError("Colombian mobile numbers must start with 3")

        return cleaned

    def __str__(self) -> str:
        """String representation."""
        return self.value


class Money(BaseModel):
    """Money value object with validation."""

    amount: float = Field(..., gt=0, description="Amount (must be positive)")
    currency: Currency = Field(default=Currency.COP, description="Currency code")

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        """Validate amount is positive and reasonable."""
        if v <= 0:
            raise ValueError("Amount must be greater than zero")

        # Minimum: 1000 COP
        if v < 1000:
            raise ValueError("Amount too low (minimum 1000 COP)")

        # Maximum: 5,000,000 COP
        if v > 5_000_000:
            raise ValueError("Amount exceeds limit (maximum 5,000,000 COP)")

        return round(v, 2)

    def __str__(self) -> str:
        """String representation."""
        return f"{self.amount:,.2f} {self.currency.value}"


# Domain Entities


class TransactionValidation(BaseModel):
    """Result of transaction validation."""

    is_valid: bool = Field(..., description="Whether transaction is valid")
    error_message: str | None = Field(None, description="Error message if invalid")


class TransactionExecution(BaseModel):
    """Result of transaction execution."""

    transaction_id: str = Field(..., description="Unique transaction ID")
    status: TransactionStatus = Field(..., description="Transaction status")
    timestamp: datetime | str = Field(..., description="Execution timestamp")
    error_message: str | None = Field(None, description="Error message if failed")

    class Config:
        """Pydantic config."""

        use_enum_values = True


class Transaction(BaseModel):
    """Transaction domain entity."""

    id: int | None = Field(None, description="Database ID")
    conversation_id: int = Field(..., description="Associated conversation ID")
    transaction_id: str | None = Field(None, description="External transaction ID")
    recipient_phone: str = Field(..., description="Recipient phone number")
    amount: float = Field(..., gt=0, description="Transaction amount")
    currency: str = Field(default="COP", description="Currency code")
    status: TransactionStatus = Field(
        default=TransactionStatus.PENDING,
        description="Transaction status",
    )
    error_message: str | None = Field(None, description="Error if failed")
    created_at: datetime | None = Field(None, description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Update timestamp")

    class Config:
        """Pydantic config."""

        from_attributes = True  # For SQLAlchemy ORM compatibility
        use_enum_values = True


class Conversation(BaseModel):
    """Conversation domain entity."""

    id: int | None = Field(None, description="Database ID")
    user_id: str = Field(..., description="User identifier")
    status: ConversationStatus = Field(
        default=ConversationStatus.ACTIVE,
        description="Conversation status",
    )
    started_at: datetime | None = Field(None, description="Start timestamp")
    ended_at: datetime | None = Field(None, description="End timestamp")
    created_at: datetime | None = Field(None, description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Update timestamp")

    # LangGraph state snapshot (stored as JSON)
    agent_state: dict[str, Any] | None = Field(
        None,
        description="LangGraph agent state snapshot",
    )

    class Config:
        """Pydantic config."""

        from_attributes = True
        use_enum_values = True


# Domain Events (for future event sourcing)


class DomainEvent(BaseModel):
    """Base domain event."""

    event_id: str = Field(..., description="Unique event ID")
    event_type: str = Field(..., description="Event type")
    aggregate_id: str = Field(..., description="Aggregate root ID")
    occurred_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When event occurred",
    )
    data: dict[str, Any] = Field(default_factory=dict, description="Event payload")


class TransactionCreated(DomainEvent):
    """Transaction created event."""

    event_type: str = Field(default="transaction.created", const=True)


class TransactionValidated(DomainEvent):
    """Transaction validated event."""

    event_type: str = Field(default="transaction.validated", const=True)


class TransactionExecuted(DomainEvent):
    """Transaction executed event."""

    event_type: str = Field(default="transaction.executed", const=True)


class TransactionFailed(DomainEvent):
    """Transaction failed event."""

    event_type: str = Field(default="transaction.failed", const=True)


class ConversationStarted(DomainEvent):
    """Conversation started event."""

    event_type: str = Field(default="conversation.started", const=True)


class ConversationEnded(DomainEvent):
    """Conversation ended event."""

    event_type: str = Field(default="conversation.ended", const=True)