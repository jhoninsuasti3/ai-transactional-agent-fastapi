"""Unit tests for TransactionAPIClient."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from apps.orchestrator.infrastructure.clients.transaction_client import TransactionAPIClient


@pytest.mark.unit
class TestTransactionAPIClient:
    """Test suite for TransactionAPIClient."""

    @pytest.fixture
    async def client(self):
        """Create test client."""
        client = TransactionAPIClient(
            base_url="http://test-api:8001", connection_timeout=1.0, read_timeout=2.0, max_retries=3
        )
        yield client
        await client.close()

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test client initializes correctly."""
        client = TransactionAPIClient(
            base_url="http://test-api:8001",
            connection_timeout=5.0,
            read_timeout=10.0,
            max_retries=3,
            circuit_breaker_threshold=5,
            circuit_breaker_timeout=60,
        )

        assert client.base_url == "http://test-api:8001"
        assert client.circuit_breaker.fail_max == 5
        assert client.circuit_breaker.reset_timeout == 60
        assert client.client is not None

        await client.close()

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test client works as async context manager."""
        async with TransactionAPIClient(base_url="http://test-api:8001") as client:
            assert client.client is not None

    @pytest.mark.asyncio
    async def test_validate_transaction_success(self, client):
        """Test successful transaction validation."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "is_valid": True,
            "validation_id": "VAL-12345",
            "message": "Can proceed",
        }

        with patch.object(client.client, "request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await client.validate_transaction(recipient_phone="3001234567", amount=50000)

            assert result["is_valid"] is True
            assert result["validation_id"] == "VAL-12345"
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_transaction_invalid(self, client):
        """Test transaction validation with invalid response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"is_valid": False, "message": "Insufficient funds"}

        with patch.object(client.client, "request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await client.validate_transaction(recipient_phone="3001234567", amount=1000000)

            assert result["is_valid"] is False
            assert "Insufficient funds" in result["message"]

    @pytest.mark.asyncio
    async def test_validate_transaction_http_error(self, client):
        """Test validation with HTTP error."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server error", request=MagicMock(), response=mock_response
        )

        with patch.object(client.client, "request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            with pytest.raises(httpx.HTTPStatusError):
                await client.validate_transaction(recipient_phone="3001234567", amount=50000)

    @pytest.mark.asyncio
    async def test_validate_transaction_timeout(self, client):
        """Test validation with timeout."""
        with patch.object(client.client, "request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = httpx.TimeoutException("Timeout")

            with pytest.raises(httpx.TimeoutException):
                await client.validate_transaction(recipient_phone="3001234567", amount=50000)

    @pytest.mark.asyncio
    async def test_execute_transaction_success(self, client):
        """Test successful transaction execution."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "transaction_id": "TXN-12345",
            "status": "completed",
            "amount": 50000,
            "currency": "COP",
            "message": "Transaction completed",
        }

        with patch.object(client.client, "request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await client.execute_transaction(
                validation_id="VAL-123", recipient_phone="3001234567", amount=50000
            )

            assert result["transaction_id"] == "TXN-12345"
            assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_get_transaction_status_success(self, client):
        """Test getting transaction status."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "transaction_id": "TXN-12345",
            "status": "completed",
            "amount": 50000,
            "currency": "COP",
            "created_at": "2025-01-27T12:00:00Z",
        }

        with patch.object(client.client, "request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await client.get_transaction_status("TXN-12345")

            assert result["transaction_id"] == "TXN-12345"
            assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_network_error_handling(self, client):
        """Test handling of network errors."""
        with patch.object(client.client, "request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = httpx.NetworkError("Connection failed")

            with pytest.raises(httpx.NetworkError):
                await client.validate_transaction(recipient_phone="3001234567", amount=50000)

    @pytest.mark.asyncio
    async def test_make_request_success(self, client):
        """Test _make_request method success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        with patch.object(client.client, "request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            response = await client._make_request("GET", "/test")

            assert response.status_code == 200
            mock_request.assert_called_once_with("GET", "/test")

    @pytest.mark.asyncio
    async def test_get_transaction_status_not_found(self, client):
        """Test getting status for non-existent transaction."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not found", request=MagicMock(), response=mock_response
        )

        with patch.object(client.client, "request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            with pytest.raises(httpx.HTTPStatusError) as exc_info:
                await client.get_transaction_status("TXN-NOTFOUND")

            assert exc_info.value.response.status_code == 404

    @pytest.mark.asyncio
    async def test_execute_transaction_http_error(self, client):
        """Test execution with HTTP error."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server error", request=MagicMock(), response=mock_response
        )

        with patch.object(client.client, "request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            with pytest.raises(httpx.HTTPStatusError):
                await client.execute_transaction(
                    validation_id="VAL-123", recipient_phone="3001234567", amount=50000
                )

    @pytest.mark.asyncio
    async def test_get_transaction_status_http_error(self, client):
        """Test get status with HTTP error."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server error", request=MagicMock(), response=mock_response
        )

        with patch.object(client.client, "request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            with pytest.raises(httpx.HTTPStatusError):
                await client.get_transaction_status("TXN-12345")
