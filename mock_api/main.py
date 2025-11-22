"""Simple Mock Transaction API - Simulates external payment service.

This is intentionally simple - the real architecture is in apps/.
"""

import asyncio
import random
import uuid
from datetime import datetime
from enum import Enum

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Mock Transaction API", version="1.0.0")

# Simple in-memory storage
transactions = {}


class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class ValidateRequest(BaseModel):
    recipient_phone: str
    amount: float = Field(gt=0)


class ValidateResponse(BaseModel):
    is_valid: bool
    error: str | None = None


class ExecuteRequest(BaseModel):
    recipient_phone: str
    amount: float = Field(gt=0)


class ExecuteResponse(BaseModel):
    transaction_id: str
    status: TransactionStatus
    timestamp: datetime


class TransactionDetail(BaseModel):
    transaction_id: str
    status: TransactionStatus
    recipient_phone: str
    amount: float
    timestamp: datetime
    error_message: str | None = None


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow()}


@app.post("/api/v1/transactions/validate")
async def validate(req: ValidateRequest) -> ValidateResponse:
    # Simulate latency 100-500ms
    await asyncio.sleep(random.uniform(0.1, 0.5))

    # Random failure 10%
    if random.random() < 0.1:
        raise HTTPException(503, "Service temporarily unavailable")

    # Simple validation
    if req.amount > 5_000_000:
        return ValidateResponse(is_valid=False, error="Amount exceeds limit")
    if req.amount < 1000:
        return ValidateResponse(is_valid=False, error="Amount too low")

    return ValidateResponse(is_valid=True)


@app.post("/api/v1/transactions/execute", status_code=201)
async def execute(req: ExecuteRequest) -> ExecuteResponse:
    # Simulate latency
    await asyncio.sleep(random.uniform(0.1, 0.5))

    # Random failure 10%
    if random.random() < 0.1:
        raise HTTPException(503, "Service temporarily unavailable")

    # Generate transaction
    tx_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
    rand = random.random()
    status = (
        TransactionStatus.COMPLETED
        if rand < 0.7
        else TransactionStatus.PENDING
        if rand < 0.9
        else TransactionStatus.FAILED
    )
    timestamp = datetime.utcnow()

    # Store
    transactions[tx_id] = TransactionDetail(
        transaction_id=tx_id,
        status=status,
        recipient_phone=req.recipient_phone,
        amount=req.amount,
        timestamp=timestamp,
        error_message="Payment declined" if status == TransactionStatus.FAILED else None,
    )

    return ExecuteResponse(transaction_id=tx_id, status=status, timestamp=timestamp)


@app.get("/api/v1/transactions/{transaction_id}")
async def get_status(transaction_id: str) -> TransactionDetail:
    # Simulate latency
    await asyncio.sleep(random.uniform(0.1, 0.5))

    # Random failure 10%
    if random.random() < 0.1:
        raise HTTPException(503, "Service temporarily unavailable")

    if transaction_id not in transactions:
        raise HTTPException(404, f"Transaction {transaction_id} not found")

    return transactions[transaction_id]