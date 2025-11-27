"""Integration tests for complete transaction flows - Happy and Unhappy Paths."""

from unittest.mock import Mock, patch

import pytest
from httpx import AsyncClient
from langchain_core.messages import AIMessage


@pytest.mark.integration
@pytest.mark.asyncio
class TestHappyPaths:
    """Integration tests for successful transaction flows."""

    @patch("apps.orchestrator.v1.routers.chat.PostgresSaver")
    @patch("apps.orchestrator.v1.routers.chat.get_agent")
    @patch("apps.orchestrator.v1.routers.chat.persistence_service")
    async def test_complete_transaction_flow_single_message(
        self, mock_persistence, mock_get_agent, mock_checkpointer, async_client: AsyncClient
    ):
        """Test complete transaction in single message - HAPPY PATH."""
        # Mock checkpointer
        mock_checkpointer_instance = Mock()
        mock_checkpointer_instance.__enter__ = Mock(return_value=mock_checkpointer_instance)
        mock_checkpointer_instance.__exit__ = Mock(return_value=None)
        mock_checkpointer_instance.setup = Mock()
        mock_checkpointer.from_conn_string.return_value = mock_checkpointer_instance

        # Mock agent - complete flow in one message
        mock_agent = Mock()
        mock_agent.invoke.return_value = {
            "messages": [AIMessage(content="Transacción completada exitosamente")],
            "phone": "3001234567",
            "amount": 50000,
            "transaction_id": "TXN-ABC123",
            "transaction_status": "completed",
            "needs_confirmation": False,
            "confirmed": True,
        }
        mock_get_agent.return_value = mock_agent

        # Mock persistence
        mock_persistence.get_or_create_conversation.return_value = "uuid-conv-123"
        mock_persistence.save_message.return_value = "uuid-msg-123"
        mock_persistence.save_transaction.return_value = "uuid-txn-123"

        # Execute
        response = await async_client.post(
            "/api/v1/chat",
            json={"message": "Enviar 50000 pesos al 3001234567", "user_id": "test-user"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["transaction_id"] == "TXN-ABC123"
        assert "conversation_id" in data
        assert "completada" in data["response"].lower()

        # Verify persistence was called
        mock_persistence.save_transaction.assert_called_once()
        mock_persistence.update_conversation_status.assert_called_once()

    @patch("apps.orchestrator.v1.routers.chat.PostgresSaver")
    @patch("apps.orchestrator.v1.routers.chat.get_agent")
    @patch("apps.orchestrator.v1.routers.chat.persistence_service")
    async def test_multi_step_transaction_flow(
        self, mock_persistence, mock_get_agent, mock_checkpointer, async_client: AsyncClient
    ):
        """Test transaction flow with multiple messages - HAPPY PATH."""
        # Mock checkpointer
        mock_checkpointer_instance = Mock()
        mock_checkpointer_instance.__enter__ = Mock(return_value=mock_checkpointer_instance)
        mock_checkpointer_instance.__exit__ = Mock(return_value=None)
        mock_checkpointer_instance.setup = Mock()
        mock_checkpointer.from_conn_string.return_value = mock_checkpointer_instance

        mock_agent = Mock()
        mock_persistence.get_or_create_conversation.return_value = "uuid-conv-456"
        mock_persistence.save_message.return_value = "uuid-msg-456"

        # Step 1: User says they want to send money
        mock_agent.invoke.return_value = {
            "messages": [AIMessage(content="¿A qué número deseas enviar?")],
            "phone": None,
            "amount": None,
        }
        mock_get_agent.return_value = mock_agent

        response1 = await async_client.post(
            "/api/v1/chat", json={"message": "Quiero enviar dinero", "user_id": "test-user"}
        )
        assert response1.status_code == 200
        conv_id = response1.json()["conversation_id"]

        # Step 2: User provides phone
        mock_agent.invoke.return_value = {
            "messages": [AIMessage(content="¿Cuánto deseas enviar?")],
            "phone": "3009876543",
            "amount": None,
        }

        response2 = await async_client.post(
            "/api/v1/chat",
            json={"message": "Al 3009876543", "conversation_id": conv_id, "user_id": "test-user"},
        )
        assert response2.status_code == 200

        # Step 3: User provides amount
        mock_agent.invoke.return_value = {
            "messages": [AIMessage(content="¿Confirmas el envío?")],
            "phone": "3009876543",
            "amount": 75000,
            "needs_confirmation": True,
        }

        response3 = await async_client.post(
            "/api/v1/chat",
            json={"message": "75000 pesos", "conversation_id": conv_id, "user_id": "test-user"},
        )
        assert response3.status_code == 200
        assert response3.json()["requires_confirmation"] is True

        # Step 4: User confirms
        mock_agent.invoke.return_value = {
            "messages": [AIMessage(content="Transacción completada")],
            "phone": "3009876543",
            "amount": 75000,
            "transaction_id": "TXN-XYZ789",
            "transaction_status": "completed",
            "confirmed": True,
        }
        mock_persistence.save_transaction.return_value = "uuid-txn-789"

        response4 = await async_client.post(
            "/api/v1/chat",
            json={"message": "Sí, confirmo", "conversation_id": conv_id, "user_id": "test-user"},
        )
        assert response4.status_code == 200
        assert response4.json()["transaction_id"] == "TXN-XYZ789"


@pytest.mark.integration
@pytest.mark.asyncio
class TestUnhappyPaths:
    """Integration tests for error scenarios and edge cases."""

    @patch("apps.orchestrator.v1.routers.chat.PostgresSaver")
    @patch("apps.orchestrator.v1.routers.chat.get_agent")
    async def test_agent_raises_exception(
        self, mock_get_agent, mock_checkpointer, async_client: AsyncClient
    ):
        """Test handling when agent raises exception - UNHAPPY PATH."""
        # Mock checkpointer
        mock_checkpointer_instance = Mock()
        mock_checkpointer_instance.__enter__ = Mock(return_value=mock_checkpointer_instance)
        mock_checkpointer_instance.__exit__ = Mock(return_value=None)
        mock_checkpointer_instance.setup = Mock()
        mock_checkpointer.from_conn_string.return_value = mock_checkpointer_instance

        # Agent raises exception
        mock_agent = Mock()
        mock_agent.invoke.side_effect = Exception("LLM service unavailable")
        mock_get_agent.return_value = mock_agent

        response = await async_client.post(
            "/api/v1/chat", json={"message": "Test", "user_id": "test-user"}
        )

        assert response.status_code == 500
        assert "error" in response.json()["detail"].lower()

    @patch("apps.orchestrator.v1.routers.chat.PostgresSaver")
    @patch("apps.orchestrator.v1.routers.chat.get_agent")
    @patch("apps.orchestrator.v1.routers.chat.persistence_service")
    async def test_persistence_fails_gracefully(
        self, mock_persistence, mock_get_agent, mock_checkpointer, async_client: AsyncClient
    ):
        """Test that persistence failure doesn't break the response - UNHAPPY PATH."""
        # Mock checkpointer
        mock_checkpointer_instance = Mock()
        mock_checkpointer_instance.__enter__ = Mock(return_value=mock_checkpointer_instance)
        mock_checkpointer_instance.__exit__ = Mock(return_value=None)
        mock_checkpointer_instance.setup = Mock()
        mock_checkpointer.from_conn_string.return_value = mock_checkpointer_instance

        # Agent works fine
        mock_agent = Mock()
        mock_agent.invoke.return_value = {
            "messages": [AIMessage(content="Respuesta del agente")],
            "phone": None,
            "amount": None,
        }
        mock_get_agent.return_value = mock_agent

        # Persistence fails
        mock_persistence.get_or_create_conversation.side_effect = Exception(
            "Database connection error"
        )

        response = await async_client.post(
            "/api/v1/chat", json={"message": "Hola", "user_id": "test-user"}
        )

        # Should still return 200 with agent response (persistence error is logged but not raised)
        assert response.status_code == 200
        assert "respuesta del agente" in response.json()["response"].lower()

    @patch("apps.orchestrator.v1.routers.chat.PostgresSaver")
    @patch("apps.orchestrator.v1.routers.chat.get_agent")
    @patch("apps.orchestrator.v1.routers.chat.persistence_service")
    async def test_user_cancels_transaction(
        self, mock_persistence, mock_get_agent, mock_checkpointer, async_client: AsyncClient
    ):
        """Test user canceling transaction - UNHAPPY PATH."""
        # Mock checkpointer
        mock_checkpointer_instance = Mock()
        mock_checkpointer_instance.__enter__ = Mock(return_value=mock_checkpointer_instance)
        mock_checkpointer_instance.__exit__ = Mock(return_value=None)
        mock_checkpointer_instance.setup = Mock()
        mock_checkpointer.from_conn_string.return_value = mock_checkpointer_instance

        mock_agent = Mock()
        mock_persistence.get_or_create_conversation.return_value = "uuid-conv-cancel"
        mock_persistence.save_message.return_value = "uuid-msg-cancel"

        # Agent indicates user canceled
        mock_agent.invoke.return_value = {
            "messages": [AIMessage(content="Transacción cancelada")],
            "phone": "3001234567",
            "amount": 50000,
            "confirmed": False,
            "needs_confirmation": True,
        }
        mock_get_agent.return_value = mock_agent

        response = await async_client.post(
            "/api/v1/chat", json={"message": "No, cancela", "user_id": "test-user"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "transaction_id" not in data or data.get("transaction_id") is None
        assert "cancel" in data["response"].lower()

    @patch("apps.orchestrator.v1.routers.chat.PostgresSaver")
    @patch("apps.orchestrator.v1.routers.chat.get_agent")
    @patch("apps.orchestrator.v1.routers.chat.persistence_service")
    async def test_invalid_phone_number_handling(
        self, mock_persistence, mock_get_agent, mock_checkpointer, async_client: AsyncClient
    ):
        """Test handling of invalid phone number - UNHAPPY PATH."""
        # Mock checkpointer
        mock_checkpointer_instance = Mock()
        mock_checkpointer_instance.__enter__ = Mock(return_value=mock_checkpointer_instance)
        mock_checkpointer_instance.__exit__ = Mock(return_value=None)
        mock_checkpointer_instance.setup = Mock()
        mock_checkpointer.from_conn_string.return_value = mock_checkpointer_instance

        mock_agent = Mock()
        mock_persistence.get_or_create_conversation.return_value = "uuid-conv-invalid"
        mock_persistence.save_message.return_value = "uuid-msg-invalid"

        # Agent detects invalid phone
        mock_agent.invoke.return_value = {
            "messages": [AIMessage(content="El número debe tener 10 dígitos")],
            "phone": None,  # Not extracted because invalid
            "amount": None,
        }
        mock_get_agent.return_value = mock_agent

        response = await async_client.post(
            "/api/v1/chat", json={"message": "Enviar al 123", "user_id": "test-user"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["metadata"].get("phone") is None

    @patch("apps.orchestrator.v1.routers.chat.PostgresSaver")
    @patch("apps.orchestrator.v1.routers.chat.get_agent")
    @patch("apps.orchestrator.v1.routers.chat.persistence_service")
    async def test_empty_message_handling(
        self, mock_persistence, mock_get_agent, mock_checkpointer, async_client: AsyncClient
    ):
        """Test handling of empty message - EDGE CASE."""
        response = await async_client.post(
            "/api/v1/chat", json={"message": "", "user_id": "test-user"}
        )

        # Empty message should fail validation (min_length=1)
        assert response.status_code == 422

    @patch("apps.orchestrator.v1.routers.chat.PostgresSaver")
    @patch("apps.orchestrator.v1.routers.chat.get_agent")
    @patch("apps.orchestrator.v1.routers.chat.persistence_service")
    async def test_very_long_message_handling(
        self, mock_persistence, mock_get_agent, mock_checkpointer, async_client: AsyncClient
    ):
        """Test handling of very long message - EDGE CASE."""
        long_message = "A" * 10000
        response = await async_client.post(
            "/api/v1/chat", json={"message": long_message, "user_id": "test-user"}
        )

        # Message exceeds max_length=1000, should fail validation
        assert response.status_code == 422

    @patch("apps.orchestrator.v1.routers.chat.PostgresSaver")
    @patch("apps.orchestrator.v1.routers.chat.get_agent")
    @patch("apps.orchestrator.v1.routers.chat.persistence_service")
    async def test_special_characters_in_message(
        self, mock_persistence, mock_get_agent, mock_checkpointer, async_client: AsyncClient
    ):
        """Test handling of special characters - EDGE CASE."""
        # Mock checkpointer
        mock_checkpointer_instance = Mock()
        mock_checkpointer_instance.__enter__ = Mock(return_value=mock_checkpointer_instance)
        mock_checkpointer_instance.__exit__ = Mock(return_value=None)
        mock_checkpointer_instance.setup = Mock()
        mock_checkpointer.from_conn_string.return_value = mock_checkpointer_instance

        mock_agent = Mock()
        mock_persistence.get_or_create_conversation.return_value = "uuid-conv-special"
        mock_persistence.save_message.return_value = "uuid-msg-special"

        mock_agent.invoke.return_value = {
            "messages": [AIMessage(content="Procesado correctamente")],
            "phone": "3001234567",
            "amount": 50000,
        }
        mock_get_agent.return_value = mock_agent

        response = await async_client.post(
            "/api/v1/chat",
            json={
                "message": "Enviar $50,000 al (300) 123-4567 por favor! 💰",
                "user_id": "test-user",
            },
        )

        # Should extract despite special formatting
        assert response.status_code == 200
