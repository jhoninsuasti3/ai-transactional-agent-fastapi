"""Transaction endpoints for Mock API."""

import asyncio
from datetime import datetime

from fastapi import APIRouter, HTTPException

from mock_api.models import (
    ExecuteRequest,
    ExecuteResponse,
    TransactionDetail,
    TransactionStatus,
    ValidateRequest,
    ValidateResponse,
)
from mock_api.utils import (
    generate_transaction_id,
    generate_validation_id,
    random_transaction_status,
    simulate_latency,
    simulate_random_failure,
)

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])

# Simple in-memory storage
transactions: dict[str, TransactionDetail] = {}
validations: dict[str, dict] = {}


@router.post("/validate", response_model=ValidateResponse)
async def validate_transaction(request: ValidateRequest) -> ValidateResponse:
    """
    Validate if a transaction can be processed.

    Simulates:
    - Latency: 100-500ms
    - Random failures: 10% probability
    - Business validations
    """
    # Simulate latency
    await simulate_latency()

    # Simulate random failures
    await simulate_random_failure()

    # Business validations
    if request.amount > 5_000_000:
        return ValidateResponse(
            is_valid=False,
            message="Amount exceeds maximum limit of 5,000,000 COP",
            validation_id=None,
        )

    if request.amount < 1000:
        return ValidateResponse(
            is_valid=False,
            message="Amount is below minimum limit of 1,000 COP",
            validation_id=None,
        )

    # Generate validation ID
    validation_id = generate_validation_id()

    # Store validation data temporarily (expires after use)
    validations[validation_id] = {
        "recipient_phone": request.recipient_phone,
        "amount": request.amount,
        "currency": request.currency,
        "created_at": datetime.utcnow(),
    }

    return ValidateResponse(
        is_valid=True,
        message="Transaction can be processed",
        validation_id=validation_id,
    )


@router.post("/execute", response_model=ExecuteResponse, status_code=201)
async def execute_transaction(request: ExecuteRequest) -> ExecuteResponse:
    """
    Execute a validated transaction.

    Simulates:
    - Latency: 100-500ms
    - Random failures: 10% probability
    - Different status outcomes: completed (70%), pending (20%), failed (10%)
    """
    # Simulate latency
    await simulate_latency()

    # Simulate random failures
    await simulate_random_failure()

    # Verify validation ID exists
    if request.validation_id not in validations:
        raise HTTPException(
            status_code=400,
            detail="Invalid validation_id. Please validate transaction first.",
        )

    # Verify validation data matches
    validation_data = validations[request.validation_id]
    if (
        validation_data["recipient_phone"] != request.recipient_phone
        or validation_data["amount"] != request.amount
    ):
        raise HTTPException(
            status_code=400, detail="Transaction data does not match validation"
        )

    # Generate transaction
    transaction_id = generate_transaction_id()
    status = TransactionStatus(random_transaction_status())
    created_at = datetime.utcnow()

    # Determine completion time and error message
    completed_at = created_at if status == TransactionStatus.COMPLETED else None
    error_message = (
        "Payment declined by recipient's bank"
        if status == TransactionStatus.FAILED
        else None
    )

    # Store transaction
    transaction = TransactionDetail(
        transaction_id=transaction_id,
        status=status,
        recipient_phone=request.recipient_phone,
        amount=request.amount,
        currency=request.currency,
        created_at=created_at,
        completed_at=completed_at,
        error_message=error_message,
    )
    transactions[transaction_id] = transaction

    # Consume validation (one-time use)
    del validations[request.validation_id]

    # For pending transactions, simulate async completion after 2-5 seconds
    if status == TransactionStatus.PENDING:
        asyncio.create_task(_complete_pending_transaction(transaction_id))

    return ExecuteResponse(
        transaction_id=transaction_id,
        status=status,
        message=f"Transaction {status.value}",
    )


@router.get("/{transaction_id}", response_model=TransactionDetail)
async def get_transaction_status(transaction_id: str) -> TransactionDetail:
    """
    Get the status and details of a transaction.

    Simulates:
    - Latency: 100-500ms
    - Random failures: 10% probability
    """
    # Simulate latency
    await simulate_latency()

    # Simulate random failures
    await simulate_random_failure()

    # Check if transaction exists
    if transaction_id not in transactions:
        raise HTTPException(
            status_code=404, detail=f"Transaction {transaction_id} not found"
        )

    return transactions[transaction_id]


async def _complete_pending_transaction(transaction_id: str) -> None:
    """
    Background task to complete pending transactions after delay.

    Args:
        transaction_id: Transaction to complete
    """
    import random

    # Wait 2-5 seconds
    await asyncio.sleep(random.uniform(2, 5))

    # Update transaction status
    if transaction_id in transactions:
        transaction = transactions[transaction_id]
        # 90% success, 10% failure for pending transactions
        if random.random() < 0.9:
            transaction.status = TransactionStatus.COMPLETED
            transaction.completed_at = datetime.utcnow()
        else:
            transaction.status = TransactionStatus.FAILED
            transaction.error_message = "Transaction timeout"
            transaction.completed_at = datetime.utcnow()