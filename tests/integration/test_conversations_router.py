"""Integration tests for conversations router."""

import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.integration
@pytest.mark.asyncio
class TestConversationsRouter:
    """Integration tests for conversations endpoint."""

    async def test_get_conversation_by_id(self, async_client: AsyncClient):
        """Test getting a conversation by ID."""
        conv_id = str(uuid4())

        response = await async_client.get(f"/api/v1/conversations/{conv_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == conv_id
        assert data["status"] == "active"
        assert isinstance(data["messages"], list)

    async def test_conversations_health_endpoint(self, async_client: AsyncClient):
        """Test conversations health endpoint."""
        response = await async_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
