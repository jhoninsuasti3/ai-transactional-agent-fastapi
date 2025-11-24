"""Transaction schemas for API v1."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TransactionStatus(str, Enum):
    """Transaction status states."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class TransactionCreate(BaseModel):
    """Request schema for creating a transaction."""

    recipient_phone: str = Field(
        ...,
        description="Recipient phone number (10 digits)",
        pattern=r"^\d{10}$",
        examples=["3001234567"],
    )
    amount: float = Field(
        ...,
        gt=0,
        description="Amount to transfer",
        examples=[50000],
    )
    currency: str = Field(
        default="COP",
        description="Currency code",
        examples=["COP"],
    )


class TransactionResponse(BaseModel):
    """Response schema for transaction."""

    transaction_id: str = Field(..., description="Unique transaction identifier")
    status: TransactionStatus = Field(..., description="Transaction status")
    recipient_phone: str = Field(..., description="Recipient phone number")
    amount: float = Field(..., description="Transaction amount")
    currency: str = Field(..., description="Currency code")
    created_at: datetime = Field(..., description="Transaction creation timestamp")
    completed_at: datetime | None = Field(
        None, description="Transaction completion timestamp"
    )
    error_message: str | None = Field(None, description="Error message if failed")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "transaction_id": "TXN-96B1049943C4",
                "status": "completed",
                "recipient_phone": "3001234567",
                "amount": 50000.0,
                "currency": "COP",
                "created_at": "2025-01-23T10:00:00.000000",
                "completed_at": "2025-01-23T10:00:05.000000",
                "error_message": None,
            }
        }


class TransactionDetail(BaseModel):
    """Detailed transaction information including conversation context."""

    transaction_id: str = Field(..., description="Unique transaction identifier")
    conversation_id: str = Field(..., description="Associated conversation ID")
    status: TransactionStatus = Field(..., description="Transaction status")
    recipient_phone: str = Field(..., description="Recipient phone number")
    amount: float = Field(..., description="Transaction amount")
    currency: str = Field(..., description="Currency code")
    created_at: datetime = Field(..., description="Transaction creation timestamp")
    completed_at: datetime | None = Field(
        None, description="Transaction completion timestamp"
    )
    error_message: str | None = Field(None, description="Error message if failed")
    metadata: dict | None = Field(None, description="Additional metadata")