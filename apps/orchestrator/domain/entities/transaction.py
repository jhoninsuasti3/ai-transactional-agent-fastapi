"""Transaction domain entity following DDD principles.

This entity represents a financial transaction in the system with complete business logic.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Self
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class TransactionStatus(str, Enum):
    """Transaction lifecycle status."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Currency(str, Enum):
    """Supported currency codes."""

    COP = "COP"  # Colombian Peso
    USD = "USD"  # US Dollar
    EUR = "EUR"  # Euro


class Transaction(BaseModel):
    """Transaction aggregate root.

    Represents a complete financial transaction with all its business rules
    and invariants enforced at the domain level.

    Attributes:
        id: Unique transaction identifier (UUID)
        external_transaction_id: ID from external payment service
        user_id: User who initiated the transaction
        recipient_phone: Phone number of the recipient
        amount: Transaction amount (positive decimal)
        currency: Currency code (COP, USD, EUR)
        status: Current transaction status
        validation_id: ID from validation service
        error_message: Error description if transaction failed
        created_at: When transaction was created
        completed_at: When transaction was completed/failed
    """

    model_config = {"from_attributes": True, "use_enum_values": True}

    # Identity
    id: UUID = Field(default_factory=uuid4, description="Unique transaction ID")
    external_transaction_id: str | None = Field(
        None,
        description="External transaction ID from payment service",
    )

    # Core attributes
    user_id: str = Field(..., min_length=1, description="User identifier")
    recipient_phone: str = Field(..., description="Recipient phone number")
    amount: float = Field(..., gt=0, description="Transaction amount")
    currency: Currency = Field(default=Currency.COP, description="Currency code")

    # Status tracking
    status: TransactionStatus = Field(
        default=TransactionStatus.PENDING,
        description="Transaction status",
    )
    validation_id: str | None = Field(
        None,
        description="Validation service ID",
    )
    error_message: str | None = Field(None, description="Error message if failed")

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Creation timestamp",
    )
    completed_at: datetime | None = Field(None, description="Completion timestamp")

    @field_validator("recipient_phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate Colombian phone number format.

        Args:
            v: Phone number string

        Returns:
            Cleaned phone number

        Raises:
            ValueError: If phone number is invalid
        """
        # Remove common separators
        cleaned = v.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

        # Must be exactly 10 digits
        if not cleaned.isdigit():
            msg = "Phone number must contain only digits"
            raise ValueError(msg)

        if len(cleaned) != 10:
            msg = "Phone number must be exactly 10 digits"
            raise ValueError(msg)

        # Colombian mobile numbers start with 3
        if not cleaned.startswith("3"):
            msg = "Colombian mobile numbers must start with 3"
            raise ValueError(msg)

        return cleaned

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        """Validate transaction amount.

        Args:
            v: Amount value

        Returns:
            Rounded amount

        Raises:
            ValueError: If amount is invalid
        """
        if v <= 0:
            msg = "Amount must be greater than zero"
            raise ValueError(msg)

        # Minimum: 1000 COP
        if v < 1000:
            msg = "Amount too low (minimum 1000 COP)"
            raise ValueError(msg)

        # Maximum: 5,000,000 COP
        if v > 5_000_000:
            msg = "Amount exceeds limit (maximum 5,000,000 COP)"
            raise ValueError(msg)

        return round(v, 2)

    # Business logic methods

    def mark_as_completed(
        self,
        external_id: str,
        completed_at: datetime | None = None,
    ) -> Self:
        """Mark transaction as successfully completed.

        Args:
            external_id: External transaction ID from payment service
            completed_at: Completion timestamp (defaults to now)

        Returns:
            Self for method chaining

        Raises:
            ValueError: If transaction cannot be completed
        """
        if self.status != TransactionStatus.PENDING:
            msg = f"Cannot complete transaction in {self.status} status"
            raise ValueError(msg)

        self.status = TransactionStatus.COMPLETED
        self.external_transaction_id = external_id
        self.completed_at = completed_at or datetime.now(UTC)
        self.error_message = None

        return self

    def mark_as_failed(self, error_message: str, failed_at: datetime | None = None) -> Self:
        """Mark transaction as failed.

        Args:
            error_message: Description of the failure
            failed_at: Failure timestamp (defaults to now)

        Returns:
            Self for method chaining
        """
        if self.status == TransactionStatus.COMPLETED:
            msg = "Cannot fail a completed transaction"
            raise ValueError(msg)

        self.status = TransactionStatus.FAILED
        self.error_message = error_message
        self.completed_at = failed_at or datetime.now(UTC)

        return self

    def mark_as_cancelled(
        self,
        reason: str,
        cancelled_at: datetime | None = None,
    ) -> Self:
        """Mark transaction as cancelled.

        Args:
            reason: Cancellation reason
            cancelled_at: Cancellation timestamp (defaults to now)

        Returns:
            Self for method chaining

        Raises:
            ValueError: If transaction cannot be cancelled
        """
        if self.status == TransactionStatus.COMPLETED:
            msg = "Cannot cancel a completed transaction"
            raise ValueError(msg)

        self.status = TransactionStatus.CANCELLED
        self.error_message = f"Cancelled: {reason}"
        self.completed_at = cancelled_at or datetime.now(UTC)

        return self

    def is_pending(self) -> bool:
        """Check if transaction is pending."""
        return self.status == TransactionStatus.PENDING

    def is_completed(self) -> bool:
        """Check if transaction is completed."""
        return self.status == TransactionStatus.COMPLETED

    def is_failed(self) -> bool:
        """Check if transaction is failed."""
        return self.status == TransactionStatus.FAILED

    def is_cancelled(self) -> bool:
        """Check if transaction is cancelled."""
        return self.status == TransactionStatus.CANCELLED

    def is_finalized(self) -> bool:
        """Check if transaction is in a final state."""
        return self.status in {
            TransactionStatus.COMPLETED,
            TransactionStatus.FAILED,
            TransactionStatus.CANCELLED,
        }

    def formatted_amount(self) -> str:
        """Get formatted amount string.

        Returns:
            Formatted amount with currency (e.g., "1,000.00 COP")
        """
        return f"{self.amount:,.2f} {self.currency.value}"

    def __str__(self) -> str:
        """String representation."""
        return (
            f"Transaction(id={self.id}, "
            f"amount={self.formatted_amount()}, "
            f"status={self.status.value})"
        )
