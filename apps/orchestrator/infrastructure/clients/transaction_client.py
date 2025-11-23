"""Resilient HTTP client for external transaction service integration.

This client implements:
- Retry pattern with exponential backoff (3 attempts: 1s → 2s → 4s)
- Circuit breaker pattern (5 failures → OPEN for 60s → HALF_OPEN)
- Timeout controls (5s connection, 10s read)
- Structured logging for observability
"""

import httpx
import structlog
from pybreaker import CircuitBreaker, CircuitBreakerError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from apps.apps.core.config import settings
from apps.apps.core.exceptions import ExternalServiceError, TransactionValidationError
from apps.apps.domain.ports.transaction_port import TransactionPort
from apps.apps.domain.models.transaction import (
    TransactionValidation,
    TransactionExecution,
    TransactionStatus as DomainTransactionStatus,
)

logger = structlog.get_logger(__name__)


class TransactionClient(TransactionPort):
    """HTTP client for transaction service with resilience patterns.

    Implements the TransactionPort interface to communicate with external
    payment processing services (simulated by Mock API).
    """

    def __init__(
        self,
        base_url: str | None = None,
        timeout: httpx.Timeout | None = None,
        max_retries: int | None = None,
        circuit_breaker_threshold: int | None = None,
    ):
        """Initialize resilient transaction client.

        Args:
            base_url: Base URL for transaction service (defaults to settings)
            timeout: HTTP timeout configuration (defaults to 5s connect, 10s read)
            max_retries: Maximum retry attempts (defaults to settings)
            circuit_breaker_threshold: Failures before circuit opens (defaults to settings)
        """
        self.base_url = base_url or settings.TRANSACTION_SERVICE_URL
        self.timeout = timeout or httpx.Timeout(
            connect=settings.HTTP_TIMEOUT_CONNECT,
            read=settings.HTTP_TIMEOUT_READ,
        )
        self.max_retries = max_retries or settings.MAX_RETRIES

        # Circuit breaker configuration
        cb_threshold = circuit_breaker_threshold or settings.CIRCUIT_BREAKER_FAILURE_THRESHOLD
        self.circuit_breaker = CircuitBreaker(
            fail_max=cb_threshold,
            reset_timeout=settings.CIRCUIT_BREAKER_RESET_TIMEOUT,
            name="transaction_service_breaker",
        )

        # HTTP client with connection pooling
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
        )

        logger.info(
            "transaction_client_initialized",
            base_url=self.base_url,
            max_retries=self.max_retries,
            circuit_breaker_threshold=cb_threshold,
        )

    async def close(self) -> None:
        """Close HTTP client and release connections."""
        await self.client.aclose()
        logger.info("transaction_client_closed")

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
        **kwargs,
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
            return response
        except httpx.TimeoutException as e:
            logger.warning(
                "request_timeout",
                method=method,
                endpoint=endpoint,
                error=str(e),
            )
            raise
        except httpx.NetworkError as e:
            logger.warning(
                "network_error",
                method=method,
                endpoint=endpoint,
                error=str(e),
            )
            raise
        except httpx.HTTPStatusError as e:
            logger.error(
                "http_error",
                method=method,
                endpoint=endpoint,
                status_code=e.response.status_code,
                error=str(e),
            )
            raise

    async def validate_transaction(
        self,
        recipient_phone: str,
        amount: float,
    ) -> TransactionValidation:
        """Validate transaction before execution.

        Args:
            recipient_phone: Recipient's phone number
            amount: Transaction amount

        Returns:
            TransactionValidation with validation result

        Raises:
            TransactionValidationError: Validation failed
            ExternalServiceError: Service unavailable or circuit open
        """
        logger.info(
            "validating_transaction",
            recipient_phone=recipient_phone,
            amount=amount,
        )

        try:
            # Circuit breaker wraps the HTTP call
            response = await self.circuit_breaker.call_async(
                self._make_request,
                "POST",
                "/api/v1/transactions/validate",
                json={
                    "recipient_phone": recipient_phone,
                    "amount": amount,
                },
            )

            data = response.json()
            validation = TransactionValidation(
                is_valid=data["is_valid"],
                error_message=data.get("error"),
            )

            logger.info(
                "transaction_validated",
                is_valid=validation.is_valid,
                error=validation.error_message,
            )

            return validation

        except CircuitBreakerError as e:
            logger.error("circuit_breaker_open", error=str(e))
            raise ExternalServiceError(
                "Transaction service temporarily unavailable (circuit open)"
            ) from e
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 503:
                raise ExternalServiceError("Transaction service unavailable") from e
            raise TransactionValidationError(f"Validation failed: {e}") from e
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            logger.error("validation_failed", error=str(e))
            raise ExternalServiceError(
                "Could not reach transaction service"
            ) from e

    async def execute_transaction(
        self,
        recipient_phone: str,
        amount: float,
    ) -> TransactionExecution:
        """Execute transaction after validation.

        Args:
            recipient_phone: Recipient's phone number
            amount: Transaction amount

        Returns:
            TransactionExecution with transaction details

        Raises:
            ExternalServiceError: Service unavailable or circuit open
        """
        logger.info(
            "executing_transaction",
            recipient_phone=recipient_phone,
            amount=amount,
        )

        try:
            response = await self.circuit_breaker.call_async(
                self._make_request,
                "POST",
                "/api/v1/transactions/execute",
                json={
                    "recipient_phone": recipient_phone,
                    "amount": amount,
                },
            )

            data = response.json()
            execution = TransactionExecution(
                transaction_id=data["transaction_id"],
                status=DomainTransactionStatus(data["status"]),
                timestamp=data["timestamp"],
            )

            logger.info(
                "transaction_executed",
                transaction_id=execution.transaction_id,
                status=execution.status.value,
            )

            return execution

        except CircuitBreakerError as e:
            logger.error("circuit_breaker_open", error=str(e))
            raise ExternalServiceError(
                "Transaction service temporarily unavailable (circuit open)"
            ) from e
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 503:
                raise ExternalServiceError("Transaction service unavailable") from e
            raise ExternalServiceError(f"Execution failed: {e}") from e
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            logger.error("execution_failed", error=str(e))
            raise ExternalServiceError(
                "Could not reach transaction service"
            ) from e

    async def get_transaction_status(
        self,
        transaction_id: str,
    ) -> TransactionExecution:
        """Get current status of a transaction.

        Args:
            transaction_id: Unique transaction identifier

        Returns:
            TransactionExecution with current status

        Raises:
            ExternalServiceError: Service unavailable or transaction not found
        """
        logger.info("getting_transaction_status", transaction_id=transaction_id)

        try:
            response = await self.circuit_breaker.call_async(
                self._make_request,
                "GET",
                f"/api/v1/transactions/{transaction_id}",
            )

            data = response.json()
            execution = TransactionExecution(
                transaction_id=data["transaction_id"],
                status=DomainTransactionStatus(data["status"]),
                timestamp=data["timestamp"],
                error_message=data.get("error_message"),
            )

            logger.info(
                "transaction_status_retrieved",
                transaction_id=execution.transaction_id,
                status=execution.status.value,
            )

            return execution

        except CircuitBreakerError as e:
            logger.error("circuit_breaker_open", error=str(e))
            raise ExternalServiceError(
                "Transaction service temporarily unavailable (circuit open)"
            ) from e
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ExternalServiceError(
                    f"Transaction {transaction_id} not found"
                ) from e
            if e.response.status_code == 503:
                raise ExternalServiceError("Transaction service unavailable") from e
            raise ExternalServiceError(f"Status check failed: {e}") from e
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            logger.error("status_check_failed", error=str(e))
            raise ExternalServiceError(
                "Could not reach transaction service"
            ) from e