"""Pydantic models for Mock Transaction API."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TransactionStatus(str, Enum):
    """Transaction status states."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class ValidateRequest(BaseModel):
    """Request model for transaction validation."""

    recipient_phone: str = Field(
        ..., description="Recipient phone number (10 digits)", pattern=r"^\d{10}$"
    )
    amount: float = Field(..., gt=0, description="Amount to transfer")
    currency: str = Field(default="COP", description="Currency code")


class ValidateResponse(BaseModel):
    """Response model for transaction validation."""

    is_valid: bool = Field(..., description="Whether transaction can be processed")
    message: str = Field(..., description="Validation message")
    validation_id: str | None = Field(
        None, description="Validation ID if successful"
    )


class ExecuteRequest(BaseModel):
    """Request model for transaction execution."""

    validation_id: str = Field(..., description="Validation ID from previous step")
    recipient_phone: str = Field(
        ..., description="Recipient phone number (10 digits)", pattern=r"^\d{10}$"
    )
    amount: float = Field(..., gt=0, description="Amount to transfer")
    currency: str = Field(default="COP", description="Currency code")


class ExecuteResponse(BaseModel):
    """Response model for transaction execution."""

    transaction_id: str = Field(..., description="Unique transaction identifier")
    status: TransactionStatus = Field(..., description="Transaction status")
    message: str = Field(..., description="Execution message")


class TransactionDetail(BaseModel):
    """Detailed transaction information."""

    transaction_id: str = Field(..., description="Unique transaction identifier")
    status: TransactionStatus = Field(..., description="Current transaction status")
    recipient_phone: str = Field(..., description="Recipient phone number")
    amount: float = Field(..., description="Transaction amount")
    currency: str = Field(..., description="Currency code")
    created_at: datetime = Field(..., description="Transaction creation timestamp")
    completed_at: datetime | None = Field(
        None, description="Transaction completion timestamp"
    )
    error_message: str | None = Field(None, description="Error message if failed")