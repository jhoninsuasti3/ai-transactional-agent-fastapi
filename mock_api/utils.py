"""Utility functions for Mock API."""

import asyncio
import random
from typing import TypeVar

from fastapi import HTTPException

T = TypeVar("T")


async def simulate_latency(min_ms: int = 100, max_ms: int = 500) -> None:
    """
    Simulate realistic API latency.

    Args:
        min_ms: Minimum latency in milliseconds
        max_ms: Maximum latency in milliseconds
    """
    latency_seconds = random.uniform(min_ms / 1000, max_ms / 1000)
    await asyncio.sleep(latency_seconds)


async def simulate_random_failure(failure_rate: float = 0.1) -> None:
    """
    Simulate random API failures.

    Args:
        failure_rate: Probability of failure (0.0 to 1.0)

    Raises:
        HTTPException: 503 Service Unavailable with configurable probability
    """
    if random.random() < failure_rate:
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable - simulated failure",
        )


def generate_validation_id() -> str:
    """Generate a unique validation ID."""
    import uuid

    return f"VAL-{uuid.uuid4().hex[:12].upper()}"


def generate_transaction_id() -> str:
    """Generate a unique transaction ID."""
    import uuid

    return f"TXN-{uuid.uuid4().hex[:12].upper()}"


def random_transaction_status() -> str:
    """
    Generate random transaction status with realistic distribution.

    Returns:
        - 70% -> "completed"
        - 20% -> "pending"
        - 10% -> "failed"
    """
    rand = random.random()
    if rand < 0.7:
        return "completed"
    if rand < 0.9:
        return "pending"
    return "failed"
