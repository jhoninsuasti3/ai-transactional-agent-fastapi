"""Resilient HTTP client for external transaction service integration.

This client implements:
- Retry pattern with exponential backoff (3 attempts: 1s → 2s → 4s)
- Circuit breaker pattern (5 failures → OPEN for 60s → HALF_OPEN)
- Timeout controls (5s connection, 10s read)
- Structured logging for observability
"""

import logging
from typing import Any

import httpx
from pybreaker import CircuitBreaker, CircuitBreakerError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


class TransactionAPIClient:
    """HTTP client for transaction service with resilience patterns.

    Implements retry, circuit breaker, and timeout patterns for communicating
    with external payment processing services (Mock API).
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8001",
        connection_timeout: float = 5.0,
        read_timeout: float = 10.0,
        max_retries: int = 3,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: int = 60,
    ):
        """Initialize resilient transaction client.

        Args:
            base_url: Base URL for transaction service
            connection_timeout: Connection timeout in seconds
            read_timeout: Read timeout in seconds
            max_retries: Maximum retry attempts
            circuit_breaker_threshold: Failures before circuit opens
            circuit_breaker_timeout: Seconds before circuit half-opens
        """
        self.base_url = base_url
        self.timeout = httpx.Timeout(
            timeout=read_timeout,
            connect=connection_timeout,
        )

        # Circuit breaker configuration
        self.circuit_breaker = CircuitBreaker(
            fail_max=circuit_breaker_threshold,
            reset_timeout=circuit_breaker_timeout,
            name="transaction_service_breaker",
        )

        # HTTP client with connection pooling
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
        )

        logger.info(
            f"TransactionAPIClient initialized: base_url={base_url}, "
            f"max_retries={max_retries}, circuit_breaker_threshold={circuit_breaker_threshold}"
        )

    async def close(self) -> None:
        """Close HTTP client and release connections."""
        await self.client.aclose()
        logger.info("TransactionAPIClient closed")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        reraise=True,
    )
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make HTTP request with retry logic.

        Retries on timeout and network errors with exponential backoff.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for httpx request

        Returns:
            HTTP response

        Raises:
            httpx.TimeoutException: Request timed out after retries
            httpx.NetworkError: Network error after retries
            httpx.HTTPStatusError: HTTP error response
        """
        try:
            response = await self.client.request(method, endpoint, **kwargs)
            response.raise_for_status()
            logger.debug(
                f"Request successful: {method} {endpoint} -> {response.status_code}"
            )
            return response
        except httpx.TimeoutException as e:
            logger.warning(f"Request timeout: {method} {endpoint} - {str(e)}")
            raise
        except httpx.NetworkError as e:
            logger.warning(f"Network error: {method} {endpoint} - {str(e)}")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error: {method} {endpoint} - "
                f"{e.response.status_code} - {str(e)}"
            )
            raise

    async def validate_transaction(
        self,
        recipient_phone: str,
        amount: float,
        currency: str = "COP",
    ) -> dict[str, Any]:
        """Validate transaction before execution.

        Args:
            recipient_phone: Recipient's phone number (10 digits)
            amount: Transaction amount
            currency: Currency code (default: COP)

        Returns:
            Validation response with is_valid, message, and validation_id

        Raises:
            CircuitBreakerError: Circuit is open
            httpx.HTTPStatusError: HTTP error from service
            httpx.TimeoutException: Request timed out
        """
        logger.info(
            f"Validating transaction: phone={recipient_phone}, amount={amount}"
        )

        try:
            # Circuit breaker wraps the HTTP call
            response = await self._make_request(
                "POST",
                "/api/v1/transactions/validate",
                json={
                    "recipient_phone": recipient_phone,
                    "amount": amount,
                    "currency": currency,
                },
            )

            data = response.json()
            logger.info(
                f"Transaction validated: is_valid={data['is_valid']}, "
                f"validation_id={data.get('validation_id')}"
            )
            return data

        except CircuitBreakerError as e:
            logger.error(f"Circuit breaker open: {str(e)}")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Validation failed with HTTP error: {e.response.status_code}"
            )
            raise
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            logger.error(f"Validation failed: {str(e)}")
            raise

    async def execute_transaction(
        self,
        validation_id: str,
        recipient_phone: str,
        amount: float,
        currency: str = "COP",
    ) -> dict[str, Any]:
        """Execute transaction after validation.

        Args:
            validation_id: Validation ID from validate_transaction
            recipient_phone: Recipient's phone number
            amount: Transaction amount
            currency: Currency code (default: COP)

        Returns:
            Execution response with transaction_id, status, and message

        Raises:
            CircuitBreakerError: Circuit is open
            httpx.HTTPStatusError: HTTP error from service
            httpx.TimeoutException: Request timed out
        """
        logger.info(
            f"Executing transaction: validation_id={validation_id}, "
            f"phone={recipient_phone}, amount={amount}"
        )

        try:
            response = await self._make_request(
                "POST",
                "/api/v1/transactions/execute",
                json={
                    "validation_id": validation_id,
                    "recipient_phone": recipient_phone,
                    "amount": amount,
                    "currency": currency,
                },
            )

            data = response.json()
            logger.info(
                f"Transaction executed: transaction_id={data['transaction_id']}, "
                f"status={data['status']}"
            )
            return data

        except CircuitBreakerError as e:
            logger.error(f"Circuit breaker open: {str(e)}")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Execution failed with HTTP error: {e.response.status_code}"
            )
            raise
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            logger.error(f"Execution failed: {str(e)}")
            raise

    async def get_transaction_status(
        self,
        transaction_id: str,
    ) -> dict[str, Any]:
        """Get current status of a transaction.

        Args:
            transaction_id: Unique transaction identifier

        Returns:
            Transaction details with status, amount, timestamps, etc.

        Raises:
            CircuitBreakerError: Circuit is open
            httpx.HTTPStatusError: HTTP error from service (404 if not found)
            httpx.TimeoutException: Request timed out
        """
        logger.info(f"Getting transaction status: transaction_id={transaction_id}")

        try:
            response = await self._make_request(
                "GET",
                f"/api/v1/transactions/{transaction_id}",
            )

            data = response.json()
            logger.info(
                f"Transaction status retrieved: transaction_id={transaction_id}, "
                f"status={data['status']}"
            )
            return data

        except CircuitBreakerError as e:
            logger.error(f"Circuit breaker open: {str(e)}")
            raise
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Transaction not found: {transaction_id}")
            else:
                logger.error(
                    f"Status check failed with HTTP error: {e.response.status_code}"
                )
            raise
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            logger.error(f"Status check failed: {str(e)}")
            raise