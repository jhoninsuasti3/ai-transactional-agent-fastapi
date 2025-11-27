"""Integration tests for transaction flows - Success and Error scenarios."""

from unittest.mock import Mock, patch

import pytest
from httpx import AsyncClient
from langchain_core.messages import AIMessage


@pytest.mark.integration
@pytest.mark.asyncio
class TestSuccessfulTransactionFlows:
    """Tests for successful transaction execution flows."""

    @patch("apps.orchestrator.v1.routers.chat.PostgresSaver")
    @patch("apps.orchestrator.v1.routers.chat.get_agent")
    @patch("apps.orchestrator.v1.routers.chat.persistence_service")
    async def test_single_message_complete_transaction(
        self, mock_persistence, mock_get_agent, mock_checkpointer, async_client: AsyncClient
    ):
        """Test: User provides phone and amount in single message, transaction completes."""
        # Setup mocks
        mock_checkpointer_instance = Mock()
        mock_checkpointer_instance.__enter__ = Mock(return_value=mock_checkpointer_instance)
        mock_checkpointer_instance.__exit__ = Mock(return_value=None)
        mock_checkpointer_instance.setup = Mock()
        mock_checkpointer.from_conn_string.return_value = mock_checkpointer_instance

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

        mock_persistence.get_or_create_conversation.return_value = "uuid-123"
        mock_persistence.save_message.return_value = "uuid-msg-123"
        mock_persistence.save_transaction.return_value = "uuid-txn-123"

        # Execute
        response = await async_client.post(
            "/api/v1/chat",
            json={"message": "Enviar 50000 pesos al 3001234567", "user_id": "user-001"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["transaction_id"] == "TXN-ABC123"
        assert "completada" in data["response"].lower()
        mock_persistence.save_transaction.assert_called_once()

    @patch("apps.orchestrator.v1.routers.chat.PostgresSaver")
    @patch("apps.orchestrator.v1.routers.chat.get_agent")
    @patch("apps.orchestrator.v1.routers.chat.persistence_service")
    async def test_multi_turn_conversation_with_confirmation(
        self, mock_persistence, mock_get_agent, mock_checkpointer, async_client: AsyncClient
    ):
        """Test: Multi-turn conversation flow with explicit confirmation step."""
        mock_checkpointer_instance = Mock()
        mock_checkpointer_instance.__enter__ = Mock(return_value=mock_checkpointer_instance)
        mock_checkpointer_instance.__exit__ = Mock(return_value=None)
        mock_checkpointer_instance.setup = Mock()
        mock_checkpointer.from_conn_string.return_value = mock_checkpointer_instance

        mock_agent = Mock()
        mock_persistence.get_or_create_conversation.return_value = "uuid-456"
        mock_persistence.save_message.return_value = "uuid-msg-456"

        # Turn 1: Ask to send money
        mock_agent.invoke.return_value = {
            "messages": [AIMessage(content="¿A qué número deseas enviar?")],
            "phone": None,
            "amount": None,
        }
        mock_get_agent.return_value = mock_agent

        r1 = await async_client.post(
            "/api/v1/chat", json={"message": "Quiero enviar dinero", "user_id": "user-002"}
        )
        conv_id = r1.json()["conversation_id"]

        # Turn 2: Provide phone and amount
        mock_agent.invoke.return_value = {
            "messages": [AIMessage(content="¿Confirmas el envío de 75000 al 3009876543?")],
            "phone": "3009876543",
            "amount": 75000,
            "needs_confirmation": True,
        }

        r2 = await async_client.post(
            "/api/v1/chat",
            json={
                "message": "3009876543 y enviar 75000",
                "conversation_id": conv_id,
                "user_id": "user-002",
            },
        )
        assert r2.json()["requires_confirmation"] is True

        # Turn 3: Confirm
        mock_agent.invoke.return_value = {
            "messages": [AIMessage(content="Transacción completada")],
            "phone": "3009876543",
            "amount": 75000,
            "transaction_id": "TXN-XYZ789",
            "transaction_status": "completed",
            "confirmed": True,
        }
        mock_persistence.save_transaction.return_value = "uuid-txn-789"

        r3 = await async_client.post(
            "/api/v1/chat",
            json={"message": "Sí, confirmo", "conversation_id": conv_id, "user_id": "user-002"},
        )
        assert r3.json()["transaction_id"] == "TXN-XYZ789"


@pytest.mark.integration
@pytest.mark.asyncio
class TestTransactionValidationErrors:
    """Tests for validation errors and business rule violations."""

    @patch("apps.orchestrator.v1.routers.chat.PostgresSaver")
    @patch("apps.orchestrator.v1.routers.chat.get_agent")
    @patch("apps.orchestrator.v1.routers.chat.persistence_service")
    async def test_invalid_phone_number_format(
        self, mock_persistence, mock_get_agent, mock_checkpointer, async_client: AsyncClient
    ):
        """Test: System rejects phone number with invalid format (not 10 digits)."""
        mock_checkpointer_instance = Mock()
        mock_checkpointer_instance.__enter__ = Mock(return_value=mock_checkpointer_instance)
        mock_checkpointer_instance.__exit__ = Mock(return_value=None)
        mock_checkpointer_instance.setup = Mock()
        mock_checkpointer.from_conn_string.return_value = mock_checkpointer_instance

        mock_agent = Mock()
        mock_persistence.get_or_create_conversation.return_value = "uuid-inv1"
        mock_persistence.save_message.return_value = "uuid-msg-inv1"

        # Agent doesn't extract invalid phone
        mock_agent.invoke.return_value = {
            "messages": [AIMessage(content="El número debe tener 10 dígitos y empezar con 3")],
            "phone": None,
            "amount": None,
        }
        mock_get_agent.return_value = mock_agent

        response = await async_client.post(
            "/api/v1/chat", json={"message": "Enviar al 123456", "user_id": "user-003"}
        )

        assert response.status_code == 200
        assert response.json()["metadata"].get("phone") is None

    @patch("apps.orchestrator.v1.routers.chat.PostgresSaver")
    @patch("apps.orchestrator.v1.routers.chat.get_agent")
    @patch("apps.orchestrator.v1.routers.chat.persistence_service")
    async def test_negative_or_zero_amount(
        self, mock_persistence, mock_get_agent, mock_checkpointer, async_client: AsyncClient
    ):
        """Test: System rejects negative or zero amounts."""
        mock_checkpointer_instance = Mock()
        mock_checkpointer_instance.__enter__ = Mock(return_value=mock_checkpointer_instance)
        mock_checkpointer_instance.__exit__ = Mock(return_value=None)
        mock_checkpointer_instance.setup = Mock()
        mock_checkpointer.from_conn_string.return_value = mock_checkpointer_instance

        mock_agent = Mock()
        mock_persistence.get_or_create_conversation.return_value = "uuid-inv2"
        mock_persistence.save_message.return_value = "uuid-msg-inv2"

        mock_agent.invoke.return_value = {
            "messages": [AIMessage(content="El monto debe ser mayor a cero")],
            "phone": "3001234567",
            "amount": None,
        }
        mock_get_agent.return_value = mock_agent

        response = await async_client.post(
            "/api/v1/chat", json={"message": "Enviar 0 pesos al 3001234567", "user_id": "user-004"}
        )

        assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.asyncio
class TestUserCancellationFlows:
    """Tests for user-initiated cancellation scenarios."""

    @patch("apps.orchestrator.v1.routers.chat.PostgresSaver")
    @patch("apps.orchestrator.v1.routers.chat.get_agent")
    @patch("apps.orchestrator.v1.routers.chat.persistence_service")
    async def test_user_cancels_before_confirmation(
        self, mock_persistence, mock_get_agent, mock_checkpointer, async_client: AsyncClient
    ):
        """Test: User says 'no' or 'cancel' when asked for confirmation."""
        mock_checkpointer_instance = Mock()
        mock_checkpointer_instance.__enter__ = Mock(return_value=mock_checkpointer_instance)
        mock_checkpointer_instance.__exit__ = Mock(return_value=None)
        mock_checkpointer_instance.setup = Mock()
        mock_checkpointer.from_conn_string.return_value = mock_checkpointer_instance

        mock_agent = Mock()
        mock_persistence.get_or_create_conversation.return_value = "uuid-cancel1"
        mock_persistence.save_message.return_value = "uuid-msg-cancel1"

        mock_agent.invoke.return_value = {
            "messages": [AIMessage(content="Transacción cancelada")],
            "phone": "3001234567",
            "amount": 50000,
            "confirmed": False,
        }
        mock_get_agent.return_value = mock_agent

        response = await async_client.post(
            "/api/v1/chat", json={"message": "No, cancela", "user_id": "user-005"}
        )

        assert response.status_code == 200
        assert (
            "transaction_id" not in response.json() or response.json().get("transaction_id") is None
        )


@pytest.mark.integration
@pytest.mark.asyncio
class TestSystemErrorHandling:
    """Tests for system error and resilience scenarios."""

    @patch("apps.orchestrator.v1.routers.chat.PostgresSaver")
    @patch("apps.orchestrator.v1.routers.chat.get_agent")
    async def test_llm_service_unavailable(
        self, mock_get_agent, mock_checkpointer, async_client: AsyncClient
    ):
        """Test: LLM service is unavailable or times out."""
        mock_checkpointer_instance = Mock()
        mock_checkpointer_instance.__enter__ = Mock(return_value=mock_checkpointer_instance)
        mock_checkpointer_instance.__exit__ = Mock(return_value=None)
        mock_checkpointer_instance.setup = Mock()
        mock_checkpointer.from_conn_string.return_value = mock_checkpointer_instance

        mock_agent = Mock()
        mock_agent.invoke.side_effect = Exception("OpenAI API timeout")
        mock_get_agent.return_value = mock_agent

        response = await async_client.post(
            "/api/v1/chat", json={"message": "Test", "user_id": "user-006"}
        )

        assert response.status_code == 500
        assert "error" in response.json()["detail"].lower()

    @patch("apps.orchestrator.v1.routers.chat.PostgresSaver")
    @patch("apps.orchestrator.v1.routers.chat.get_agent")
    @patch("apps.orchestrator.v1.routers.chat.persistence_service")
    async def test_database_persistence_fails(
        self, mock_persistence, mock_get_agent, mock_checkpointer, async_client: AsyncClient
    ):
        """Test: Database is down but response is still delivered."""
        mock_checkpointer_instance = Mock()
        mock_checkpointer_instance.__enter__ = Mock(return_value=mock_checkpointer_instance)
        mock_checkpointer_instance.__exit__ = Mock(return_value=None)
        mock_checkpointer_instance.setup = Mock()
        mock_checkpointer.from_conn_string.return_value = mock_checkpointer_instance

        mock_agent = Mock()
        mock_agent.invoke.return_value = {
            "messages": [AIMessage(content="Hola")],
            "phone": None,
            "amount": None,
        }
        mock_get_agent.return_value = mock_agent

        # Persistence fails
        mock_persistence.get_or_create_conversation.side_effect = Exception("DB connection lost")

        response = await async_client.post(
            "/api/v1/chat", json={"message": "Hola", "user_id": "user-007"}
        )

        # Should still return agent response
        assert response.status_code == 200
        assert "hola" in response.json()["response"].lower()


@pytest.mark.integration
@pytest.mark.asyncio
class TestEdgeCasesAndBoundaryConditions:
    """Tests for edge cases and boundary conditions."""

    @patch("apps.orchestrator.v1.routers.chat.PostgresSaver")
    @patch("apps.orchestrator.v1.routers.chat.get_agent")
    @patch("apps.orchestrator.v1.routers.chat.persistence_service")
    async def test_empty_message(
        self, mock_persistence, mock_get_agent, mock_checkpointer, async_client: AsyncClient
    ):
        """Test: User sends empty message - should return validation error."""
        response = await async_client.post(
            "/api/v1/chat", json={"message": "", "user_id": "user-008"}
        )

        # Empty message should fail validation (min_length=1)
        assert response.status_code == 422

    @patch("apps.orchestrator.v1.routers.chat.PostgresSaver")
    @patch("apps.orchestrator.v1.routers.chat.get_agent")
    @patch("apps.orchestrator.v1.routers.chat.persistence_service")
    async def test_extremely_long_message(
        self, mock_persistence, mock_get_agent, mock_checkpointer, async_client: AsyncClient
    ):
        """Test: User sends very long message - should return validation error."""
        long_message = "A" * 10000
        response = await async_client.post(
            "/api/v1/chat", json={"message": long_message, "user_id": "user-009"}
        )

        # Message exceeds max_length=1000, should fail validation
        assert response.status_code == 422

    @patch("apps.orchestrator.v1.routers.chat.PostgresSaver")
    @patch("apps.orchestrator.v1.routers.chat.get_agent")
    @patch("apps.orchestrator.v1.routers.chat.persistence_service")
    async def test_special_characters_and_emojis(
        self, mock_persistence, mock_get_agent, mock_checkpointer, async_client: AsyncClient
    ):
        """Test: Message contains special characters, emojis, and formatting."""
        mock_checkpointer_instance = Mock()
        mock_checkpointer_instance.__enter__ = Mock(return_value=mock_checkpointer_instance)
        mock_checkpointer_instance.__exit__ = Mock(return_value=None)
        mock_checkpointer_instance.setup = Mock()
        mock_checkpointer.from_conn_string.return_value = mock_checkpointer_instance

        mock_agent = Mock()
        mock_persistence.get_or_create_conversation.return_value = "uuid-edge3"
        mock_persistence.save_message.return_value = "uuid-msg-edge3"

        mock_agent.invoke.return_value = {
            "messages": [AIMessage(content="Procesado")],
            "phone": "3001234567",
            "amount": 50000,
        }
        mock_get_agent.return_value = mock_agent

        response = await async_client.post(
            "/api/v1/chat",
            json={"message": "Enviar $50,000 al (300) 123-4567 💰🎉", "user_id": "user-010"},
        )

        assert response.status_code == 200
