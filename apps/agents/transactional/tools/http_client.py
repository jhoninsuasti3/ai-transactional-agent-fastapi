"""Resilient HTTP client for Mock Transaction API.

Implements:
- Retry pattern with exponential backoff
- Circuit breaker
- Timeouts
- Structured logging
"""

import structlog
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
import httpx
from pybreaker import CircuitBreaker

from apps.orchestrator.settings import settings

logger = structlog.get_logger(__name__)


# Circuit breaker configuration
transaction_api_breaker = CircuitBreaker(
    fail_max=settings.CIRCUIT_BREAKER_FAILURE_THRESHOLD,
    reset_timeout=settings.CIRCUIT_BREAKER_RESET_TIMEOUT,
    name="transaction_api"
)


class TransactionAPIClient:
    """Resilient HTTP client for Transaction Mock API."""

    def __init__(self):
        self.base_url = settings.TRANSACTION_SERVICE_URL
        self.timeout = httpx.Timeout(
            connect=settings.HTTP_TIMEOUT_CONNECT,
            read=settings.HTTP_TIMEOUT_READ,
            write=settings.HTTP_TIMEOUT_CONNECT,
            pool=5.0
        )

    @retry(
        stop=stop_after_attempt(settings.MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        reraise=True,
    )
    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> dict:
        """Make HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST)
            endpoint: API endpoint path
            **kwargs: Additional arguments for httpx

        Returns:
            dict: Response JSON data

        Raises:
            httpx.HTTPError: On HTTP errors
            httpx.TimeoutException: On timeout
        """
        url = f"{self.base_url}{endpoint}"

        logger.info(
            "http_request",
            method=method,
            url=url,
            **kwargs
        )

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.request(method, url, **kwargs)
                response.raise_for_status()

                logger.info(
                    "http_response",
                    status_code=response.status_code,
                    url=url
                )

                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(
                "http_error",
                status_code=e.response.status_code,
                url=url,
                error=str(e)
            )
            raise

        except (httpx.RequestError, httpx.TimeoutException) as e:
            logger.error(
                "http_request_failed",
                url=url,
                error=str(e)
            )
            raise

    @transaction_api_breaker
    def post(self, endpoint: str, json: dict) -> dict:
        """Make POST request with circuit breaker.

        Args:
            endpoint: API endpoint path
            json: Request body

        Returns:
            dict: Response JSON
        """
        return self._make_request("POST", endpoint, json=json)

    @transaction_api_breaker
    def get(self, endpoint: str) -> dict:
        """Make GET request with circuit breaker.

        Args:
            endpoint: API endpoint path

        Returns:
            dict: Response JSON
        """
        return self._make_request("GET", endpoint)


# Singleton instance
transaction_client = TransactionAPIClient()
