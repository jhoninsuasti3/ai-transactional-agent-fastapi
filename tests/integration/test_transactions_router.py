"""Integration tests for transactions router."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
class TestTransactionsRouter:
    """Integration tests for transactions endpoint."""

    @patch("apps.orchestrator.v1.routers.transactions.transaction_client")
    async def test_get_transaction_by_id(self, mock_client, async_client: AsyncClient):
        """Test getting a transaction by ID."""
        mock_client.get_transaction_status = AsyncMock(
            return_value={
                "transaction_id": "TXN-123",
                "status": "completed",
                "recipient_phone": "3001234567",
                "amount": 50000,
                "currency": "COP",
                "created_at": "2025-01-01T00:00:00",
                "completed_at": "2025-01-01T00:01:00",
            }
        )

        response = await async_client.get("/api/v1/transactions/TXN-123")

        assert response.status_code == 200
        data = response.json()
        assert data["transaction_id"] == "TXN-123"
        assert data["status"] == "completed"

    @patch("apps.orchestrator.v1.routers.transactions.transaction_client")
    async def test_get_transaction_not_found(self, mock_client, async_client: AsyncClient):
        """Test getting a non-existent transaction."""
        mock_client.get_transaction_status = AsyncMock(
            side_effect=Exception("Transaction not found")
        )

        response = await async_client.get("/api/v1/transactions/TXN-NONEXISTENT")

        assert response.status_code == 404

    @patch("apps.orchestrator.v1.routers.transactions.transaction_client")
    async def test_get_transaction_service_unavailable(
        self, mock_client, async_client: AsyncClient
    ):
        """Test handling when transaction service is unavailable."""
        mock_client.get_transaction_status = AsyncMock(side_effect=Exception("Service unavailable"))

        response = await async_client.get("/api/v1/transactions/TXN-123")

        assert response.status_code == 503

    async def test_transactions_health_endpoint(self, async_client: AsyncClient):
        """Test transactions health endpoint."""
        response = await async_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
