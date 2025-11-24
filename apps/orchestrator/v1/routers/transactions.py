"""Transactions router for API v1."""

from fastapi import APIRouter, HTTPException

from apps.orchestrator.core.config import settings
from apps.orchestrator.infrastructure.clients.transaction_client import (
    TransactionAPIClient,
)
from apps.orchestrator.v1.schemas import TransactionResponse

router = APIRouter(prefix="/transactions", tags=["transactions"])

# Initialize transaction client with settings
transaction_client = TransactionAPIClient(
    base_url=settings.TRANSACTION_SERVICE_URL,
    connection_timeout=settings.HTTP_TIMEOUT_CONNECT,
    read_timeout=settings.HTTP_TIMEOUT_READ,
    max_retries=settings.MAX_RETRIES,
    circuit_breaker_threshold=settings.CIRCUIT_BREAKER_FAILURE_THRESHOLD,
    circuit_breaker_timeout=settings.CIRCUIT_BREAKER_RESET_TIMEOUT,
)


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: str) -> TransactionResponse:
    """
    Get transaction details by ID.

    Args:
        transaction_id: Unique transaction identifier

    Returns:
        Transaction details with status, amount, timestamps, etc.

    Raises:
        HTTPException 404: Transaction not found
        HTTPException 503: External service unavailable
    """
    try:
        # Call Mock API through resilient client
        data = await transaction_client.get_transaction_status(transaction_id)

        # Map to our response schema
        return TransactionResponse(
            transaction_id=data["transaction_id"],
            status=data["status"],
            recipient_phone=data["recipient_phone"],
            amount=data["amount"],
            currency=data["currency"],
            created_at=data["created_at"],
            completed_at=data.get("completed_at"),
            error_message=data.get("error_message"),
        )

    except Exception as e:
        # Handle different error types
        error_msg = str(e)

        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} not found")

        if "unavailable" in error_msg.lower() or "circuit" in error_msg.lower():
            raise HTTPException(
                status_code=503,
                detail="Transaction service temporarily unavailable",
            )

        # Generic error
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve transaction: {error_msg}",
        )


@router.get("/health")
async def transactions_health():
    """Health check for transactions router."""
    return {
        "status": "healthy",
        "router": "transactions",
        "version": "v1",
        "mock_api_connected": True,
    }