"""End-to-end tests for complete transaction flow."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from apps.orchestrator.v1.routers.chat import router as chat_router


@pytest.fixture
def test_app():
    """Create test FastAPI app."""
    app = FastAPI()
    app.include_router(chat_router, prefix="/api/v1")
    return app


@pytest.fixture
def client(test_app):
    """Create test client."""
    return TestClient(test_app)


@pytest.mark.e2e
class TestCompleteTransactionFlow:
    """Test suite for end-to-end transaction flow."""

    @patch('apps.orchestrator.v1.routers.chat.agent')
    @patch('apps.orchestrator.v1.routers.chat._get_checkpointer')
    def test_complete_successful_transaction_flow(self, mock_checkpointer, mock_agent, client):
        """Test complete successful transaction from greeting to completion."""
        mock_checkpointer.return_value = MagicMock()

        # Step 1: Initial greeting
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

        response = client.post("/api/v1/chat", json={
            "message": "Hola",
            "user_id": "user-test-123"
        })

        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        conversation_id = data["conversation_id"]

        # Step 2: User provides phone and amount
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Enviar 50000 a 3001234567"},
                {"role": "assistant", "content": "¿Confirmas la transacción de $50,000 COP a 3001234567?"}
            ],
            "phone": "3001234567",
            "amount": 50000,
            "needs_confirmation": True,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        response = client.post("/api/v1/chat", json={
            "message": "Enviar 50000 a 3001234567",
            "conversation_id": conversation_id,
            "user_id": "user-test-123"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["requires_confirmation"] is True
        assert data["metadata"]["phone"] == "3001234567"
        assert data["metadata"]["amount"] == 50000

        # Step 3: User confirms transaction
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Sí, confirmo"},
                {"role": "assistant", "content": "Transacción completada exitosamente ID: TXN-12345"}
            ],
            "phone": "3001234567",
            "amount": 50000,
            "needs_confirmation": False,
            "confirmed": True,
            "transaction_id": "TXN-12345",
            "transaction_status": "completed",
        }

        response = client.post("/api/v1/chat", json={
            "message": "Sí, confirmo",
            "conversation_id": conversation_id,
            "user_id": "user-test-123"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["transaction_id"] == "TXN-12345"
        assert data["requires_confirmation"] is False
        assert data["metadata"]["transaction_status"] == "completed"

    @patch('apps.orchestrator.v1.routers.chat.agent')
    @patch('apps.orchestrator.v1.routers.chat._get_checkpointer')
    def test_transaction_cancelled_by_user(self, mock_checkpointer, mock_agent, client):
        """Test transaction flow when user cancels."""
        mock_checkpointer.return_value = MagicMock()

        # Step 1: User provides transaction details
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Enviar 50000 a 3001234567"},
                {"role": "assistant", "content": "¿Confirmas?"}
            ],
            "phone": "3001234567",
            "amount": 50000,
            "needs_confirmation": True,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        response = client.post("/api/v1/chat", json={
            "message": "Enviar 50000 a 3001234567",
            "user_id": "user-test-123"
        })

        assert response.status_code == 200
        conversation_id = response.json()["conversation_id"]

        # Step 2: User cancels
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "No, cancelar"},
                {"role": "assistant", "content": "Transacción cancelada"}
            ],
            "phone": "3001234567",
            "amount": 50000,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": "cancelled",
        }

        response = client.post("/api/v1/chat", json={
            "message": "No, cancelar",
            "conversation_id": conversation_id,
            "user_id": "user-test-123"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["transaction_id"] is None
        assert data["metadata"]["transaction_status"] == "cancelled"

    @patch('apps.orchestrator.v1.routers.chat.agent')
    @patch('apps.orchestrator.v1.routers.chat._get_checkpointer')
    def test_transaction_fails_validation(self, mock_checkpointer, mock_agent, client):
        """Test transaction flow when validation fails."""
        mock_checkpointer.return_value = MagicMock()

        # User provides details but validation fails
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Enviar 10000000 a 3001234567"},
                {"role": "assistant", "content": "No se puede procesar: Insufficient funds"}
            ],
            "phone": "3001234567",
            "amount": 10000000,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": "validation_failed",
        }

        response = client.post("/api/v1/chat", json={
            "message": "Enviar 10000000 a 3001234567",
            "user_id": "user-test-123"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["transaction_id"] is None
        assert data["requires_confirmation"] is False

    @patch('apps.orchestrator.v1.routers.chat.agent')
    @patch('apps.orchestrator.v1.routers.chat._get_checkpointer')
    def test_multi_step_transaction_collection(self, mock_checkpointer, mock_agent, client):
        """Test transaction with multi-step data collection."""
        mock_checkpointer.return_value = MagicMock()

        # Step 1: User says they want to send money
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Quiero enviar dinero"},
                {"role": "assistant", "content": "¿A qué número?"}
            ],
            "phone": None,
            "amount": None,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        response = client.post("/api/v1/chat", json={
            "message": "Quiero enviar dinero",
            "user_id": "user-test-123"
        })

        assert response.status_code == 200
        conversation_id = response.json()["conversation_id"]

        # Step 2: User provides phone
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "3001234567"},
                {"role": "assistant", "content": "¿Cuánto quieres enviar?"}
            ],
            "phone": "3001234567",
            "amount": None,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        response = client.post("/api/v1/chat", json={
            "message": "3001234567",
            "conversation_id": conversation_id,
            "user_id": "user-test-123"
        })

        assert response.status_code == 200
        assert response.json()["metadata"]["phone"] == "3001234567"

        # Step 3: User provides amount
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "50000"},
                {"role": "assistant", "content": "¿Confirmas $50,000 a 3001234567?"}
            ],
            "phone": "3001234567",
            "amount": 50000,
            "needs_confirmation": True,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        response = client.post("/api/v1/chat", json={
            "message": "50000",
            "conversation_id": conversation_id,
            "user_id": "user-test-123"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["requires_confirmation"] is True
        assert data["metadata"]["amount"] == 50000
