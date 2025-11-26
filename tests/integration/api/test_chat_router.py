"""Integration tests for chat router."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

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
class TestChatRouter:
    """Test suite for chat router endpoints."""

    def test_chat_health_endpoint(self, client):
        """Test chat health check endpoint."""
        response = client.get("/api/v1/chat/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["router"] == "chat"
        assert data["agent_integrated"] is True
        assert data["langgraph_agent"] == "transactional"

    @patch('apps.orchestrator.v1.routers.chat.agent')
    @patch('apps.orchestrator.v1.routers.chat._get_checkpointer')
    def test_chat_endpoint_with_mock_agent(self, mock_checkpointer, mock_agent, client):
        """Test chat endpoint with mocked agent."""
        # Mock agent response
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Hola"},
                {"role": "assistant", "content": "Hola! Cómo puedo ayudarte?"}
            ],
            "phone": None,
            "amount": None,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        # Mock checkpointer
        mock_checkpointer.return_value = MagicMock()

        # Make request
        payload = {
            "message": "Hola",
            "user_id": "user-123"
        }

        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "response" in data
        assert "conversation_id" in data
        assert data["requires_confirmation"] is False

    @patch('apps.orchestrator.v1.routers.chat.agent')
    @patch('apps.orchestrator.v1.routers.chat._get_checkpointer')
    def test_chat_endpoint_with_transaction(self, mock_checkpointer, mock_agent, client):
        """Test chat endpoint with transaction initiated."""
        # Mock agent response with transaction
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Enviar 50000 a 3001234567"},
                {"role": "assistant", "content": "¿Confirmas la transacción?"}
            ],
            "phone": "3001234567",
            "amount": 50000,
            "needs_confirmation": True,
            "confirmed": False,
            "transaction_id": "TXN-12345",
            "transaction_status": "pending",
        }

        mock_checkpointer.return_value = MagicMock()

        payload = {
            "message": "Enviar 50000 a 3001234567",
            "user_id": "user-123"
        }

        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["transaction_id"] == "TXN-12345"
        assert data["requires_confirmation"] is True
        assert "metadata" in data
        assert data["metadata"]["phone"] == "3001234567"
        assert data["metadata"]["amount"] == 50000

    def test_chat_endpoint_missing_message(self, client):
        """Test chat endpoint with missing message."""
        payload = {
            "user_id": "user-123"
        }

        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 422  # Validation error

    def test_chat_endpoint_empty_message(self, client):
        """Test chat endpoint with empty message."""
        payload = {
            "message": "",
            "user_id": "user-123"
        }

        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 422  # Validation error

    def test_chat_endpoint_message_too_long(self, client):
        """Test chat endpoint with message exceeding max length."""
        payload = {
            "message": "a" * 1001,  # Max is 1000
            "user_id": "user-123"
        }

        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 422  # Validation error

    @patch('apps.orchestrator.v1.routers.chat.agent')
    @patch('apps.orchestrator.v1.routers.chat._get_checkpointer')
    def test_chat_endpoint_with_conversation_id(self, mock_checkpointer, mock_agent, client):
        """Test chat endpoint with existing conversation ID."""
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Continuar"},
                {"role": "assistant", "content": "Ok, continuemos"}
            ],
            "phone": None,
            "amount": None,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        mock_checkpointer.return_value = MagicMock()

        payload = {
            "message": "Continuar",
            "conversation_id": "conv-existing-123",
            "user_id": "user-123"
        }

        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["conversation_id"] == "conv-existing-123"

    @patch('apps.orchestrator.v1.routers.chat.agent')
    @patch('apps.orchestrator.v1.routers.chat._get_checkpointer')
    def test_chat_endpoint_agent_error_handling(self, mock_checkpointer, mock_agent, client):
        """Test chat endpoint handles agent errors gracefully."""
        # Mock agent to raise exception
        mock_agent.invoke.side_effect = Exception("Agent error")
        mock_checkpointer.return_value = MagicMock()

        payload = {
            "message": "Hola",
            "user_id": "user-123"
        }

        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 500

        data = response.json()
        assert "detail" in data
