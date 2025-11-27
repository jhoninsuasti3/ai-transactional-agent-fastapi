"""Unit tests for persistence service."""

from datetime import datetime
from unittest.mock import MagicMock, Mock, patch
from uuid import UUID, uuid4

import pytest

from apps.orchestrator.services.persistence_service import PersistenceService


@pytest.mark.unit
class TestPersistenceService:
    """Test suite for persistence service."""

    @patch("apps.orchestrator.services.persistence_service.create_engine")
    @patch("apps.orchestrator.services.persistence_service.sessionmaker")
    def test_persistence_service_init(self, mock_sessionmaker, mock_create_engine):
        """Test persistence service initializes with sync database connection."""
        service = PersistenceService()

        assert service is not None
        mock_create_engine.assert_called_once()
        mock_sessionmaker.assert_called_once()

    @patch("apps.orchestrator.services.persistence_service.create_engine")
    @patch("apps.orchestrator.services.persistence_service.sessionmaker")
    def test_get_or_create_conversation_creates_new(self, mock_sessionmaker, mock_create_engine):
        """Test get_or_create_conversation creates new conversation."""
        # Setup mocks
        mock_session = MagicMock()
        mock_sessionmaker.return_value.return_value.__enter__.return_value = mock_session
        mock_session.execute.return_value.scalar_one_or_none.return_value = None

        mock_conversation = Mock()
        mock_conversation.id = uuid4()

        def mock_add(obj):
            obj.id = mock_conversation.id

        mock_session.add = mock_add
        mock_session.refresh = Mock()

        service = PersistenceService()

        # Execute
        result = service.get_or_create_conversation("test-conv-id", "user-123")

        # Assert
        assert isinstance(result, UUID)
        mock_session.commit.assert_called()

    @patch("apps.orchestrator.services.persistence_service.create_engine")
    @patch("apps.orchestrator.services.persistence_service.sessionmaker")
    def test_save_message(self, mock_sessionmaker, mock_create_engine):
        """Test save_message creates message record."""
        # Setup mocks
        mock_session = MagicMock()
        mock_sessionmaker.return_value.return_value.__enter__.return_value = mock_session

        mock_message = Mock()
        mock_message.id = uuid4()

        def mock_add(obj):
            obj.id = mock_message.id

        mock_session.add = mock_add
        mock_session.refresh = Mock()

        service = PersistenceService()

        # Execute
        conv_id = uuid4()
        result = service.save_message(
            conversation_id=conv_id, role="user", content="Test message", metadata={"key": "value"}
        )

        # Assert
        assert isinstance(result, UUID)
        mock_session.commit.assert_called()

    @patch("apps.orchestrator.services.persistence_service.create_engine")
    @patch("apps.orchestrator.services.persistence_service.sessionmaker")
    def test_save_transaction(self, mock_sessionmaker, mock_create_engine):
        """Test save_transaction creates transaction record."""
        # Setup mocks
        mock_session = MagicMock()
        mock_sessionmaker.return_value.return_value.__enter__.return_value = mock_session

        mock_transaction = Mock()
        mock_transaction.id = uuid4()

        def mock_add(obj):
            obj.id = mock_transaction.id

        mock_session.add = mock_add
        mock_session.refresh = Mock()

        service = PersistenceService()

        # Execute
        conv_id = uuid4()
        result = service.save_transaction(
            conversation_id=conv_id,
            user_id="user-123",
            external_transaction_id="TXN-123",
            recipient_phone="3001234567",
            amount=50000.0,
            status="completed",
        )

        # Assert
        assert isinstance(result, UUID)
        mock_session.commit.assert_called()

    @patch("apps.orchestrator.services.persistence_service.create_engine")
    @patch("apps.orchestrator.services.persistence_service.sessionmaker")
    def test_update_conversation_status(self, mock_sessionmaker, mock_create_engine):
        """Test update_conversation_status updates existing conversation."""
        # Setup mocks
        mock_session = MagicMock()
        mock_sessionmaker.return_value.return_value.__enter__.return_value = mock_session

        mock_conversation = Mock()
        mock_conversation.status = "active"
        mock_conversation.ended_at = None
        mock_session.execute.return_value.scalar_one_or_none.return_value = mock_conversation

        service = PersistenceService()

        # Execute
        conv_id = uuid4()
        ended_at = datetime.utcnow()
        service.update_conversation_status(
            conversation_id=conv_id, status="completed", ended_at=ended_at
        )

        # Assert
        assert mock_conversation.status == "completed"
        assert mock_conversation.ended_at == ended_at
        mock_session.commit.assert_called()

    @patch("apps.orchestrator.services.persistence_service.create_engine")
    @patch("apps.orchestrator.services.persistence_service.sessionmaker")
    def test_update_conversation_status_conversation_not_found(
        self, mock_sessionmaker, mock_create_engine
    ):
        """Test update_conversation_status handles conversation not found gracefully."""
        # Setup mocks
        mock_session = MagicMock()
        mock_sessionmaker.return_value.return_value.__enter__.return_value = mock_session
        mock_session.execute.return_value.scalar_one_or_none.return_value = None

        service = PersistenceService()

        # Execute - should not raise exception
        conv_id = uuid4()
        service.update_conversation_status(conversation_id=conv_id, status="completed")

        # Assert - commit should not be called
        mock_session.commit.assert_not_called()

    @patch("apps.orchestrator.services.persistence_service.create_engine")
    @patch("apps.orchestrator.services.persistence_service.sessionmaker")
    def test_save_message_without_metadata(self, mock_sessionmaker, mock_create_engine):
        """Test save_message works without metadata."""
        # Setup mocks
        mock_session = MagicMock()
        mock_sessionmaker.return_value.return_value.__enter__.return_value = mock_session

        mock_message = Mock()
        mock_message.id = uuid4()

        def mock_add(obj):
            obj.id = mock_message.id

        mock_session.add = mock_add
        mock_session.refresh = Mock()

        service = PersistenceService()

        # Execute
        conv_id = uuid4()
        result = service.save_message(
            conversation_id=conv_id, role="assistant", content="Test response"
        )

        # Assert
        assert isinstance(result, UUID)
        mock_session.commit.assert_called()

    @patch("apps.orchestrator.services.persistence_service.create_engine")
    @patch("apps.orchestrator.services.persistence_service.sessionmaker")
    def test_save_transaction_with_error(self, mock_sessionmaker, mock_create_engine):
        """Test save_transaction handles error_message parameter."""
        # Setup mocks
        mock_session = MagicMock()
        mock_sessionmaker.return_value.return_value.__enter__.return_value = mock_session

        mock_transaction = Mock()
        mock_transaction.id = uuid4()

        def mock_add(obj):
            obj.id = mock_transaction.id

        mock_session.add = mock_add
        mock_session.refresh = Mock()

        service = PersistenceService()

        # Execute
        conv_id = uuid4()
        result = service.save_transaction(
            conversation_id=conv_id,
            user_id="user-123",
            external_transaction_id="TXN-FAIL",
            recipient_phone="3001234567",
            amount=50000.0,
            status="failed",
            error_message="Transaction failed",
        )

        # Assert
        assert isinstance(result, UUID)
        mock_session.commit.assert_called()
