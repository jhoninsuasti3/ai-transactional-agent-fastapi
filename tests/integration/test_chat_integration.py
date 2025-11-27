"""Integration tests for chat router with mocked dependencies."""

from unittest.mock import Mock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
class TestChatIntegration:
    """Integration tests for chat endpoint."""

    @patch("apps.orchestrator.v1.routers.chat.PostgresSaver")
    @patch("apps.orchestrator.v1.routers.chat.get_agent")
    @patch("apps.orchestrator.v1.routers.chat.persistence_service")
    async def test_chat_creates_conversation(
        self, mock_persistence, mock_get_agent, mock_checkpointer, async_client: AsyncClient
    ):
        """Test chat endpoint creates conversation successfully."""
        # Mock checkpointer
        mock_checkpointer_instance = Mock()
        mock_checkpointer_instance.__enter__ = Mock(return_value=mock_checkpointer_instance)
        mock_checkpointer_instance.__exit__ = Mock(return_value=None)
        mock_checkpointer_instance.setup = Mock()
        mock_checkpointer.from_conn_string.return_value = mock_checkpointer_instance

        # Setup mocks
        mock_agent = Mock()
        mock_agent.invoke.return_value = {
            "messages": [Mock(content="¿En qué puedo ayudarte?")],
            "phone": None,
            "amount": None,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_status": None,
        }
        mock_get_agent.return_value = mock_agent

        mock_persistence.get_or_create_conversation.return_value = "conv-uuid-123"
        mock_persistence.save_message.return_value = "msg-uuid-123"

        # Execute
        response = await async_client.post(
            "/api/v1/chat", json={"message": "Hola", "user_id": "test-user"}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert "response" in data

    @patch("apps.orchestrator.v1.routers.chat.PostgresSaver")
    @patch("apps.orchestrator.v1.routers.chat.get_agent")
    @patch("apps.orchestrator.v1.routers.chat.persistence_service")
    async def test_chat_handles_transaction_completion(
        self, mock_persistence, mock_get_agent, mock_checkpointer, async_client: AsyncClient
    ):
        """Test chat endpoint handles completed transaction."""
        # Mock checkpointer
        mock_checkpointer_instance = Mock()
        mock_checkpointer_instance.__enter__ = Mock(return_value=mock_checkpointer_instance)
        mock_checkpointer_instance.__exit__ = Mock(return_value=None)
        mock_checkpointer_instance.setup = Mock()
        mock_checkpointer.from_conn_string.return_value = mock_checkpointer_instance

        # Setup mocks
        mock_agent = Mock()
        mock_agent.invoke.return_value = {
            "messages": [Mock(content="Transacción completada")],
            "phone": "3001234567",
            "amount": 50000,
            "transaction_id": "TXN-123",
            "transaction_status": "completed",
            "needs_confirmation": False,
            "confirmed": True,
        }
        mock_get_agent.return_value = mock_agent

        mock_persistence.get_or_create_conversation.return_value = "conv-uuid-123"
        mock_persistence.save_message.return_value = "msg-uuid-123"
        mock_persistence.save_transaction.return_value = "txn-uuid-123"

        # Execute
        response = await async_client.post(
            "/api/v1/chat",
            json={"message": "Sí confirmo", "user_id": "test-user", "conversation_id": "conv-123"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data.get("transaction_id") == "TXN-123"

        # Verify transaction was saved
        mock_persistence.save_transaction.assert_called_once()
        mock_persistence.update_conversation_status.assert_called_once()

    @patch("apps.orchestrator.v1.routers.chat.get_agent")
    async def test_chat_handles_errors_gracefully(self, mock_get_agent, async_client: AsyncClient):
        """Test chat endpoint handles errors gracefully."""
        # Setup mock to raise exception
        mock_get_agent.side_effect = Exception("Test error")

        # Execute
        response = await async_client.post(
            "/api/v1/chat", json={"message": "Test", "user_id": "test-user"}
        )

        # Assert
        assert response.status_code == 500
        assert "error" in response.json()["detail"].lower()

    async def test_chat_health_endpoint(self, async_client: AsyncClient):
        """Test chat health endpoint."""
        response = await async_client.get("/api/v1/chat/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["agent_integrated"] is True
