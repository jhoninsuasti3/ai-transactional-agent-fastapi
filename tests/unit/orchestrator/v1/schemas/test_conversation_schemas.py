"""Unit tests for conversation schemas."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from apps.orchestrator.v1.schemas.conversation import (
    ConversationStatus,
    MessageRole,
    Message,
    ConversationDetail,
    ConversationSummary,
)


@pytest.mark.unit
class TestConversationStatus:
    """Test suite for ConversationStatus enum."""

    def test_conversation_status_values(self):
        """Test conversation status enum values."""
        assert ConversationStatus.ACTIVE == "active"
        assert ConversationStatus.COMPLETED == "completed"
        assert ConversationStatus.ABANDONED == "abandoned"


@pytest.mark.unit
class TestMessageRole:
    """Test suite for MessageRole enum."""

    def test_message_role_values(self):
        """Test message role enum values."""
        assert MessageRole.USER == "user"
        assert MessageRole.ASSISTANT == "assistant"
        assert MessageRole.SYSTEM == "system"


@pytest.mark.unit
class TestMessage:
    """Test suite for Message schema."""

    def test_valid_message_user(self):
        """Test valid user message creation."""
        message = Message(
            role=MessageRole.USER,
            content="Hola, quiero enviar dinero"
        )
        assert message.role == MessageRole.USER
        assert message.content == "Hola, quiero enviar dinero"
        assert isinstance(message.timestamp, datetime)
        assert message.metadata is None

    def test_valid_message_assistant(self):
        """Test valid assistant message creation."""
        message = Message(
            role=MessageRole.ASSISTANT,
            content="Claro, puedo ayudarte con eso"
        )
        assert message.role == MessageRole.ASSISTANT

    def test_message_with_metadata(self):
        """Test message with metadata."""
        metadata = {"intent": "send_money", "confidence": 0.95}
        message = Message(
            role=MessageRole.USER,
            content="Enviar 50000",
            metadata=metadata
        )
        assert message.metadata == metadata
        assert message.metadata["confidence"] == 0.95

    def test_message_with_custom_timestamp(self):
        """Test message with custom timestamp."""
        custom_time = datetime(2025, 1, 25, 10, 0, 0)
        message = Message(
            role=MessageRole.SYSTEM,
            content="Sistema iniciado",
            timestamp=custom_time
        )
        assert message.timestamp == custom_time

    def test_missing_required_fields_fail(self):
        """Test that missing required fields fail validation."""
        with pytest.raises(ValidationError):
            Message(role=MessageRole.USER)


@pytest.mark.unit
class TestConversationDetail:
    """Test suite for ConversationDetail schema."""

    def test_valid_conversation_detail(self):
        """Test valid conversation detail creation."""
        messages = [
            Message(role=MessageRole.USER, content="Hola"),
            Message(role=MessageRole.ASSISTANT, content="Hola! En qué puedo ayudarte?")
        ]
        conversation = ConversationDetail(
            conversation_id="conv-123",
            user_id="user-456",
            status=ConversationStatus.ACTIVE,
            messages=messages,
            started_at=datetime.utcnow()
        )
        assert conversation.conversation_id == "conv-123"
        assert conversation.user_id == "user-456"
        assert conversation.status == ConversationStatus.ACTIVE
        assert len(conversation.messages) == 2
        assert conversation.ended_at is None
        assert len(conversation.transaction_ids) == 0

    def test_conversation_detail_with_transactions(self):
        """Test conversation detail with transaction IDs."""
        messages = [Message(role=MessageRole.USER, content="Test")]
        conversation = ConversationDetail(
            conversation_id="conv-123",
            user_id="user-456",
            status=ConversationStatus.COMPLETED,
            messages=messages,
            started_at=datetime.utcnow(),
            ended_at=datetime.utcnow(),
            transaction_ids=["TXN-111", "TXN-222"]
        )
        assert conversation.status == ConversationStatus.COMPLETED
        assert conversation.ended_at is not None
        assert len(conversation.transaction_ids) == 2
        assert "TXN-111" in conversation.transaction_ids

    def test_empty_messages_allowed(self):
        """Test that empty messages list is allowed."""
        conversation = ConversationDetail(
            conversation_id="conv-123",
            user_id="user-456",
            status=ConversationStatus.ACTIVE,
            messages=[],
            started_at=datetime.utcnow()
        )
        assert len(conversation.messages) == 0


@pytest.mark.unit
class TestConversationSummary:
    """Test suite for ConversationSummary schema."""

    def test_valid_conversation_summary(self):
        """Test valid conversation summary creation."""
        summary = ConversationSummary(
            conversation_id="conv-123",
            user_id="user-456",
            status=ConversationStatus.ACTIVE,
            message_count=5,
            started_at=datetime.utcnow()
        )
        assert summary.conversation_id == "conv-123"
        assert summary.user_id == "user-456"
        assert summary.message_count == 5
        assert summary.ended_at is None
        assert summary.last_message is None

    def test_conversation_summary_with_last_message(self):
        """Test conversation summary with last message preview."""
        summary = ConversationSummary(
            conversation_id="conv-123",
            user_id="user-456",
            status=ConversationStatus.COMPLETED,
            message_count=10,
            started_at=datetime.utcnow(),
            ended_at=datetime.utcnow(),
            last_message="Gracias por usar nuestro servicio"
        )
        assert summary.status == ConversationStatus.COMPLETED
        assert summary.message_count == 10
        assert summary.last_message == "Gracias por usar nuestro servicio"

    def test_abandoned_conversation(self):
        """Test abandoned conversation summary."""
        summary = ConversationSummary(
            conversation_id="conv-123",
            user_id="user-456",
            status=ConversationStatus.ABANDONED,
            message_count=3,
            started_at=datetime.utcnow(),
            ended_at=datetime.utcnow()
        )
        assert summary.status == ConversationStatus.ABANDONED
