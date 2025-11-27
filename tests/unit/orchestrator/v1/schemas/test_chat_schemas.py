"""Unit tests for chat schemas."""

import pytest
from pydantic import ValidationError

from apps.orchestrator.v1.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConfirmationRequest,
    ConfirmationResponse,
)


@pytest.mark.unit
class TestChatRequest:
    """Test suite for ChatRequest schema."""

    def test_valid_chat_request(self):
        """Test valid chat request creation."""
        request = ChatRequest(message="Hola, quiero enviar dinero", user_id="user-123")
        assert request.message == "Hola, quiero enviar dinero"
        assert request.user_id == "user-123"
        assert request.conversation_id is None

    def test_chat_request_with_conversation_id(self):
        """Test chat request with existing conversation ID."""
        request = ChatRequest(
            message="Confirmar transacción", conversation_id="conv-456", user_id="user-123"
        )
        assert request.conversation_id == "conv-456"

    def test_empty_message_fails(self):
        """Test that empty message fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(message="", user_id="user-123")
        assert "message" in str(exc_info.value)

    def test_message_too_long_fails(self):
        """Test that message exceeding max length fails."""
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(message="a" * 1001, user_id="user-123")
        assert "message" in str(exc_info.value)

    def test_missing_user_id_fails(self):
        """Test that missing user_id fails validation."""
        with pytest.raises(ValidationError):
            ChatRequest(message="Hola")


@pytest.mark.unit
class TestChatResponse:
    """Test suite for ChatResponse schema."""

    def test_valid_chat_response(self):
        """Test valid chat response creation."""
        response = ChatResponse(response="Hola! En qué puedo ayudarte?", conversation_id="conv-123")
        assert response.response == "Hola! En qué puedo ayudarte?"
        assert response.conversation_id == "conv-123"
        assert response.transaction_id is None
        assert response.requires_confirmation is False

    def test_chat_response_with_transaction(self):
        """Test chat response with transaction ID."""
        response = ChatResponse(
            response="Transacción iniciada",
            conversation_id="conv-123",
            transaction_id="TXN-12345",
            requires_confirmation=True,
            metadata={"amount": 50000, "phone": "3001234567"},
        )
        assert response.transaction_id == "TXN-12345"
        assert response.requires_confirmation is True
        assert response.metadata["amount"] == 50000


@pytest.mark.unit
class TestConfirmationRequest:
    """Test suite for ConfirmationRequest schema."""

    def test_valid_confirmation_request(self):
        """Test valid confirmation request."""
        request = ConfirmationRequest(conversation_id="conv-123", confirmed=True)
        assert request.conversation_id == "conv-123"
        assert request.confirmed is True

    def test_confirmation_rejected(self):
        """Test confirmation rejected."""
        request = ConfirmationRequest(conversation_id="conv-123", confirmed=False)
        assert request.confirmed is False

    def test_missing_fields_fail(self):
        """Test that missing required fields fail."""
        with pytest.raises(ValidationError):
            ConfirmationRequest(conversation_id="conv-123")


@pytest.mark.unit
class TestConfirmationResponse:
    """Test suite for ConfirmationResponse schema."""

    def test_valid_confirmation_response(self):
        """Test valid confirmation response."""
        response = ConfirmationResponse(
            response="Transacción completada exitosamente",
            transaction_id="TXN-12345",
            status="completed",
        )
        assert response.transaction_id == "TXN-12345"
        assert response.status == "completed"

    def test_confirmation_response_failed(self):
        """Test confirmation response with failed status."""
        response = ConfirmationResponse(response="La transacción falló", status="failed")
        assert response.transaction_id is None
        assert response.status == "failed"
