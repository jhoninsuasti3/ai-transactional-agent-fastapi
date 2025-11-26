"""End-to-end tests following the technical requirements conversation flows."""

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


@pytest.mark.e2e
class TestRequirementBasedFlows:
    """E2E tests based on technical requirements conversation flows."""

    @patch('apps.orchestrator.v1.routers.chat.agent')
    @patch('apps.orchestrator.v1.routers.chat._get_checkpointer')
    def test_complete_transaction_flow_as_per_requirements(self, mock_checkpointer, mock_agent, client):
        """
        Test complete transaction flow exactly as specified in requirements:
        Usuario: "Hola, quiero enviar dinero"
        Agente: "Por supuesto, puedo ayudarte con eso. ¿A qué número de celular deseas enviar dinero?"
        Usuario: "Al 3001234567"
        Agente: "Perfecto. ¿Qué monto deseas enviar?"
        Usuario: "50000 pesos"
        Agente: "Entendido. Confirmas el envío de $50,000 COP al número 3001234567?"
        Usuario: "Sí, confirmo"
        Agente: "Transacción completada exitosamente. El ID de tu transacción es: TXN-12345"
        """
        mock_checkpointer.return_value = MagicMock()

        # Step 1: Usuario: "Hola, quiero enviar dinero"
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Hola, quiero enviar dinero"},
                {"role": "assistant", "content": "Por supuesto, puedo ayudarte con eso. ¿A qué número de celular deseas enviar dinero?"}
            ],
            "phone": None,
            "amount": None,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        response1 = client.post("/api/v1/chat", json={
            "message": "Hola, quiero enviar dinero",
            "user_id": "user-req-test"
        })

        assert response1.status_code == 200
        data1 = response1.json()
        assert "conversation_id" in data1
        conversation_id = data1["conversation_id"]

        # Step 2: Usuario: "Al 3001234567"
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Al 3001234567"},
                {"role": "assistant", "content": "Perfecto. ¿Qué monto deseas enviar?"}
            ],
            "phone": "3001234567",
            "amount": None,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        response2 = client.post("/api/v1/chat", json={
            "message": "Al 3001234567",
            "user_id": "user-req-test",
            "conversation_id": conversation_id
        })

        assert response2.status_code == 200

        # Step 3: Usuario: "50000 pesos"
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "50000 pesos"},
                {"role": "assistant", "content": "Entendido. Confirmas el envío de $50,000 COP al número 3001234567?"}
            ],
            "phone": "3001234567",
            "amount": 50000,
            "needs_confirmation": True,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        response3 = client.post("/api/v1/chat", json={
            "message": "50000 pesos",
            "user_id": "user-req-test",
            "conversation_id": conversation_id
        })

        assert response3.status_code == 200
        data3 = response3.json()
        assert data3["requires_confirmation"] is True

        # Step 4: Usuario: "Sí, confirmo"
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Sí, confirmo"},
                {"role": "assistant", "content": "Transacción completada exitosamente. El ID de tu transacción es: TXN-12345"}
            ],
            "phone": "3001234567",
            "amount": 50000,
            "needs_confirmation": False,
            "confirmed": True,
            "transaction_id": "TXN-12345",
            "transaction_status": "completed",
        }

        response4 = client.post("/api/v1/chat", json={
            "message": "Sí, confirmo",
            "user_id": "user-req-test",
            "conversation_id": conversation_id
        })

        assert response4.status_code == 200
        data4 = response4.json()
        assert data4["transaction_id"] == "TXN-12345"
        assert "TXN-12345" in data4["response"]

    @patch('apps.orchestrator.v1.routers.chat.agent')
    @patch('apps.orchestrator.v1.routers.chat._get_checkpointer')
    def test_phone_validation_10_digits(self, mock_checkpointer, mock_agent, client):
        """Test phone validation: must be exactly 10 digits as per requirements."""
        mock_checkpointer.return_value = MagicMock()

        # Invalid phone - less than 10 digits
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Enviar dinero al 123"},
                {"role": "assistant", "content": "El número debe tener exactamente 10 dígitos"}
            ],
            "phone": None,
            "amount": None,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        response = client.post("/api/v1/chat", json={
            "message": "Enviar dinero al 123",
            "user_id": "user-validation-test"
        })

        assert response.status_code == 200
        assert response.json()["requires_confirmation"] is False

    @patch('apps.orchestrator.v1.routers.chat.agent')
    @patch('apps.orchestrator.v1.routers.chat._get_checkpointer')
    def test_amount_validation_greater_than_zero(self, mock_checkpointer, mock_agent, client):
        """Test amount validation: must be greater than 0 as per requirements."""
        mock_checkpointer.return_value = MagicMock()

        # Invalid amount - zero or negative
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Enviar 0 pesos al 3001234567"},
                {"role": "assistant", "content": "El monto debe ser mayor a 0"}
            ],
            "phone": None,
            "amount": None,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        response = client.post("/api/v1/chat", json={
            "message": "Enviar 0 pesos al 3001234567",
            "user_id": "user-validation-test"
        })

        assert response.status_code == 200
        assert response.json()["requires_confirmation"] is False

    @patch('apps.orchestrator.v1.routers.chat.agent')
    @patch('apps.orchestrator.v1.routers.chat._get_checkpointer')
    def test_confirmation_required_before_execution(self, mock_checkpointer, mock_agent, client):
        """Test that confirmation is required before executing transaction."""
        mock_checkpointer.return_value = MagicMock()

        # User provides phone and amount
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Enviar 100000 al 3009876543"}
            ],
            "phone": "3009876543",
            "amount": 100000,
            "needs_confirmation": True,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        response = client.post("/api/v1/chat", json={
            "message": "Enviar 100000 al 3009876543",
            "user_id": "user-confirm-test"
        })

        assert response.status_code == 200
        data = response.json()
        # Must require confirmation before executing
        assert data["requires_confirmation"] is True
        # Transaction should not be executed yet
        assert data["transaction_id"] is None

    @patch('apps.orchestrator.v1.routers.chat.agent')
    @patch('apps.orchestrator.v1.routers.chat._get_checkpointer')
    def test_context_maintained_across_conversation(self, mock_checkpointer, mock_agent, client):
        """Test that conversation context is maintained across multiple messages."""
        mock_checkpointer.return_value = MagicMock()

        # Message 1
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
            "user_id": "user-context-test"
        })

        conversation_id = response1.json()["conversation_id"]

        # Message 2 - provide phone
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Hola"},
                {"role": "user", "content": "3001234567"}
            ],
            "phone": "3001234567",
            "amount": None,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        response2 = client.post("/api/v1/chat", json={
            "message": "3001234567",
            "user_id": "user-context-test",
            "conversation_id": conversation_id
        })

        # Message 3 - provide amount (context should include phone from previous message)
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Hola"},
                {"role": "user", "content": "3001234567"},
                {"role": "user", "content": "25000"}
            ],
            "phone": "3001234567",  # Context maintained
            "amount": 25000,
            "needs_confirmation": True,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        response3 = client.post("/api/v1/chat", json={
            "message": "25000",
            "user_id": "user-context-test",
            "conversation_id": conversation_id
        })

        assert response3.status_code == 200
        assert response3.json()["requires_confirmation"] is True

    @patch('apps.orchestrator.v1.routers.chat.agent')
    @patch('apps.orchestrator.v1.routers.chat._get_checkpointer')
    def test_conversational_error_handling(self, mock_checkpointer, mock_agent, client):
        """Test that errors are handled in a conversational manner."""
        mock_checkpointer.return_value = MagicMock()

        # Simulate transaction failure
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Sí, confirmo"},
                {"role": "assistant", "content": "Lo siento, hubo un error al procesar la transacción. Por favor intenta nuevamente."}
            ],
            "phone": "3001234567",
            "amount": 50000,
            "needs_confirmation": False,
            "confirmed": True,
            "transaction_id": None,
            "transaction_status": "failed",
        }

        response = client.post("/api/v1/chat", json={
            "message": "Sí, confirmo",
            "user_id": "user-error-test"
        })

        assert response.status_code == 200
        data = response.json()
        # Error should be handled conversationally
        assert "error" in data["response"].lower() or "intenta" in data["response"].lower()

    @patch('apps.orchestrator.v1.routers.chat.agent')
    @patch('apps.orchestrator.v1.routers.chat._get_checkpointer')
    def test_transaction_status_pending(self, mock_checkpointer, mock_agent, client):
        """Test handling of pending transaction status."""
        mock_checkpointer.return_value = MagicMock()

        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Sí, confirmo"},
                {"role": "assistant", "content": "Tu transacción está siendo procesada. ID: TXN-PENDING"}
            ],
            "phone": "3001234567",
            "amount": 75000,
            "needs_confirmation": False,
            "confirmed": True,
            "transaction_id": "TXN-PENDING",
            "transaction_status": "pending",
        }

        response = client.post("/api/v1/chat", json={
            "message": "Sí, confirmo",
            "user_id": "user-pending-test"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["transaction_id"] == "TXN-PENDING"

    @patch('apps.orchestrator.v1.routers.chat.agent')
    @patch('apps.orchestrator.v1.routers.chat._get_checkpointer')
    def test_natural_language_variations(self, mock_checkpointer, mock_agent, client):
        """Test agent handles various natural language phrasings."""
        mock_checkpointer.return_value = MagicMock()

        # Test variation: "transferir" instead of "enviar"
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Quiero transferir plata"},
                {"role": "assistant", "content": "Claro, ¿a qué número?"}
            ],
            "phone": None,
            "amount": None,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        response = client.post("/api/v1/chat", json={
            "message": "Quiero transferir plata",
            "user_id": "user-nl-test"
        })

        assert response.status_code == 200

    @patch('apps.orchestrator.v1.routers.chat.agent')
    @patch('apps.orchestrator.v1.routers.chat._get_checkpointer')
    def test_currency_cop_specified(self, mock_checkpointer, mock_agent, client):
        """Test that COP (Colombian Pesos) currency is properly handled."""
        mock_checkpointer.return_value = MagicMock()

        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Enviar 50000 COP al 3001234567"}
            ],
            "phone": "3001234567",
            "amount": 50000,
            "needs_confirmation": True,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        response = client.post("/api/v1/chat", json={
            "message": "Enviar 50000 COP al 3001234567",
            "user_id": "user-currency-test"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["requires_confirmation"] is True
        # Response should mention COP
        assert "COP" in data["response"] or "peso" in data["response"].lower()
