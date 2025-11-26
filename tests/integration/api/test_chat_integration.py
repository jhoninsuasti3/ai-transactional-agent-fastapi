"""Comprehensive integration tests for chat endpoint."""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import AsyncMock, patch, MagicMock

from apps.orchestrator.v1.routers.chat import router


@pytest.fixture
def test_app():
    """Create test FastAPI app with chat router."""
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return app


@pytest.fixture
def client(test_app):
    """Create test client."""
    return TestClient(test_app)


@pytest.mark.integration
class TestChatIntegrationFull:
    """Comprehensive integration test suite for chat endpoint."""

    @patch('apps.orchestrator.v1.routers.chat.agent')
    @patch('apps.orchestrator.v1.routers.chat._get_checkpointer')
    def test_chat_greeting_flow(self, mock_checkpointer, mock_agent, client):
        """Test greeting conversation flow."""
        mock_checkpointer.return_value = MagicMock()
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Hola"},
                {"role": "assistant", "content": "¡Hola! ¿En qué puedo ayudarte?"}
            ],
            "phone": None,
            "amount": None,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        payload = {
            "message": "Hola",
            "user_id": "user-test-123"
        }

        response = client.post("/api/v1/chat", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "conversation_id" in data
        assert data["requires_confirmation"] is False
        assert data["transaction_id"] is None

    @patch('apps.orchestrator.v1.routers.chat.agent')
    @patch('apps.orchestrator.v1.routers.chat._get_checkpointer')
    def test_chat_extract_transaction_info(self, mock_checkpointer, mock_agent, client):
        """Test extracting transaction information."""
        mock_checkpointer.return_value = MagicMock()
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Quiero enviar 50000 al 3001234567"},
                {"role": "assistant", "content": "Entendido, vas a enviar 50,000 COP a 3001234567"}
            ],
            "phone": "3001234567",
            "amount": 50000,
            "needs_confirmation": True,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        payload = {
            "message": "Quiero enviar 50000 al 3001234567",
            "user_id": "user-test-123"
        }

        response = client.post("/api/v1/chat", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["requires_confirmation"] is True
        assert "50,000" in data["response"] or "50000" in data["response"]

    @patch('apps.orchestrator.v1.routers.chat.agent')
    @patch('apps.orchestrator.v1.routers.chat._get_checkpointer')
    def test_chat_confirm_transaction(self, mock_checkpointer, mock_agent, client):
        """Test confirming a transaction."""
        mock_checkpointer.return_value = MagicMock()
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Sí, confirmo"},
                {"role": "assistant", "content": "Transacción completada exitosamente"}
            ],
            "phone": "3001234567",
            "amount": 50000,
            "needs_confirmation": False,
            "confirmed": True,
            "transaction_id": "TXN-12345",
            "transaction_status": "completed",
        }

        payload = {
            "message": "Sí, confirmo",
            "user_id": "user-test-123",
            "conversation_id": "conv-test-123"
        }

        response = client.post("/api/v1/chat", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["transaction_id"] == "TXN-12345"
        assert data["requires_confirmation"] is False

    @patch('apps.orchestrator.v1.routers.chat.agent')
    @patch('apps.orchestrator.v1.routers.chat._get_checkpointer')
    def test_chat_cancel_transaction(self, mock_checkpointer, mock_agent, client):
        """Test cancelling a transaction."""
        mock_checkpointer.return_value = MagicMock()
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "No, cancela"},
                {"role": "assistant", "content": "Transacción cancelada"}
            ],
            "phone": None,
            "amount": None,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        payload = {
            "message": "No, cancela",
            "user_id": "user-test-123",
            "conversation_id": "conv-test-123"
        }

        response = client.post("/api/v1/chat", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["transaction_id"] is None

    @patch('apps.orchestrator.v1.routers.chat.agent')
    @patch('apps.orchestrator.v1.routers.chat._get_checkpointer')
    def test_chat_with_metadata(self, mock_checkpointer, mock_agent, client):
        """Test chat response includes metadata."""
        mock_checkpointer.return_value = MagicMock()
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Estado de cuenta"}
            ],
            "phone": None,
            "amount": None,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        payload = {
            "message": "Estado de cuenta",
            "user_id": "user-test-123"
        }

        response = client.post("/api/v1/chat", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "metadata" in data
        assert isinstance(data["metadata"], dict)

    @patch('apps.orchestrator.v1.routers.chat.agent')
    @patch('apps.orchestrator.v1.routers.chat._get_checkpointer')
    def test_chat_invalid_amount(self, mock_checkpointer, mock_agent, client):
        """Test handling invalid transaction amount."""
        mock_checkpointer.return_value = MagicMock()
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Enviar -1000 al 3001234567"},
                {"role": "assistant", "content": "El monto debe ser positivo"}
            ],
            "phone": None,
            "amount": None,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        payload = {
            "message": "Enviar -1000 al 3001234567",
            "user_id": "user-test-123"
        }

        response = client.post("/api/v1/chat", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["requires_confirmation"] is False

    @patch('apps.orchestrator.v1.routers.chat.agent')
    @patch('apps.orchestrator.v1.routers.chat._get_checkpointer')
    def test_chat_invalid_phone(self, mock_checkpointer, mock_agent, client):
        """Test handling invalid phone number."""
        mock_checkpointer.return_value = MagicMock()
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Enviar 50000 al 123"},
                {"role": "assistant", "content": "El número debe tener 10 dígitos"}
            ],
            "phone": None,
            "amount": None,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        payload = {
            "message": "Enviar 50000 al 123",
            "user_id": "user-test-123"
        }

        response = client.post("/api/v1/chat", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["requires_confirmation"] is False

    @patch('apps.orchestrator.v1.routers.chat.agent')
    @patch('apps.orchestrator.v1.routers.chat._get_checkpointer')
    def test_chat_conversation_continuity(self, mock_checkpointer, mock_agent, client):
        """Test conversation maintains context."""
        mock_checkpointer.return_value = MagicMock()

        # First message
        mock_agent.invoke.return_value = {
            "messages": [{"role": "user", "content": "Hola"}],
            "phone": None,
            "amount": None,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        response1 = client.post("/api/v1/chat", json={
            "message": "Hola",
            "user_id": "user-test-123"
        })

        conv_id = response1.json()["conversation_id"]

        # Second message in same conversation
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Hola"},
                {"role": "assistant", "content": "Hola!"},
                {"role": "user", "content": "Enviar 10000"}
            ],
            "phone": None,
            "amount": 10000,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        response2 = client.post("/api/v1/chat", json={
            "message": "Enviar 10000",
            "user_id": "user-test-123",
            "conversation_id": conv_id
        })

        assert response2.status_code == 200
        assert response2.json()["conversation_id"] == conv_id

    @patch('apps.orchestrator.v1.routers.chat.agent')
    @patch('apps.orchestrator.v1.routers.chat._get_checkpointer')
    def test_chat_empty_message_validation(self, mock_checkpointer, mock_agent, client):
        """Test validation for empty messages."""
        payload = {
            "message": "",
            "user_id": "user-test-123"
        }

        response = client.post("/api/v1/chat", json=payload)

        # Should fail validation
        assert response.status_code == 422

    @patch('apps.orchestrator.v1.routers.chat.agent')
    @patch('apps.orchestrator.v1.routers.chat._get_checkpointer')
    def test_chat_missing_user_id(self, mock_checkpointer, mock_agent, client):
        """Test validation for missing user_id."""
        payload = {
            "message": "Hola"
        }

        response = client.post("/api/v1/chat", json=payload)

        # Should fail validation
        assert response.status_code == 422

    @patch('apps.orchestrator.v1.routers.chat.agent')
    @patch('apps.orchestrator.v1.routers.chat._get_checkpointer')
    def test_chat_long_message(self, mock_checkpointer, mock_agent, client):
        """Test handling very long messages."""
        mock_checkpointer.return_value = MagicMock()
        mock_agent.invoke.return_value = {
            "messages": [{"role": "user", "content": "a" * 1000}],
            "phone": None,
            "amount": None,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        payload = {
            "message": "a" * 1000,
            "user_id": "user-test-123"
        }

        response = client.post("/api/v1/chat", json=payload)

        assert response.status_code == 200

    @patch('apps.orchestrator.v1.routers.chat.agent')
    @patch('apps.orchestrator.v1.routers.chat._get_checkpointer')
    def test_chat_special_characters(self, mock_checkpointer, mock_agent, client):
        """Test handling special characters in messages."""
        mock_checkpointer.return_value = MagicMock()
        mock_agent.invoke.return_value = {
            "messages": [{"role": "user", "content": "¡Hola! ¿Cómo estás? #test @user"}],
            "phone": None,
            "amount": None,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        payload = {
            "message": "¡Hola! ¿Cómo estás? #test @user",
            "user_id": "user-test-123"
        }

        response = client.post("/api/v1/chat", json=payload)

        assert response.status_code == 200

    @patch('apps.orchestrator.v1.routers.chat.agent')
    @patch('apps.orchestrator.v1.routers.chat._get_checkpointer')
    def test_chat_multiple_amounts_in_message(self, mock_checkpointer, mock_agent, client):
        """Test handling multiple amounts in one message."""
        mock_checkpointer.return_value = MagicMock()
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Enviar 50000 o 60000?"},
                {"role": "assistant", "content": "Por favor especifica un solo monto"}
            ],
            "phone": None,
            "amount": None,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        payload = {
            "message": "Enviar 50000 o 60000?",
            "user_id": "user-test-123"
        }

        response = client.post("/api/v1/chat", json=payload)

        assert response.status_code == 200
