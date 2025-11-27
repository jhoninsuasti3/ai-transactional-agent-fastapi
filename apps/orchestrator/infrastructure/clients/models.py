"""Response models for external transaction API.

These Pydantic models provide type safety and validation for responses
from the external transaction service (Mock API).
"""

from pydantic import BaseModel, Field


class ValidationResponse(BaseModel):
    """Response from transaction validation endpoint.

    Example:
        {
            "is_valid": true,
            "validation_id": "val_abc123",
            "message": "Transaction validated successfully"
        }
    """

    is_valid: bool = Field(description="Whether the transaction is valid")
    validation_id: str | None = Field(default=None, description="Unique validation identifier")
    message: str = Field(description="Validation result message")


class ExecutionResponse(BaseModel):
    """Response from transaction execution endpoint.

    Example:
        {
            "transaction_id": "txn_xyz789",
            "status": "completed",
            "amount": 100.50,
            "currency": "USD",
            "message": "Transaction executed successfully"
        }
    """

    transaction_id: str = Field(description="Unique transaction identifier")
    status: str = Field(description="Transaction status (completed, failed, etc.)")
    amount: float = Field(description="Transaction amount")
    currency: str = Field(description="Transaction currency code (USD, EUR, etc.)")
    message: str = Field(description="Execution result message")


class StatusResponse(BaseModel):
    """Response from transaction status endpoint.

    Example:
        {
            "transaction_id": "txn_xyz789",
            "status": "completed",
            "amount": 100.50,
            "currency": "USD",
            "created_at": "2025-01-15T10:30:00Z"
        }
    """

    transaction_id: str = Field(description="Unique transaction identifier")
    status: str = Field(description="Current transaction status")
    amount: float = Field(description="Transaction amount")
    currency: str = Field(description="Transaction currency code")
    created_at: str = Field(description="Transaction creation timestamp (ISO 8601)")
