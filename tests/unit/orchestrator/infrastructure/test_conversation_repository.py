"""Unit tests for ConversationRepository."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock
from uuid import uuid4

import pytest

from apps.orchestrator.domain.entities import (
    Conversation,
    ConversationStatus,
    Message,
    MessageRole,
)
from apps.orchestrator.infrastructure.persistence.models import (
    ConversationORM,
    MessageORM,
)
from apps.orchestrator.infrastructure.persistence.repositories.conversation_repository import (
    ConversationRepository,
)


@pytest.mark.unit
class TestConversationRepository:
    """Test suite for ConversationRepository."""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession."""
        session = AsyncMock()
        session.add = Mock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        session.delete = AsyncMock()
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def sample_conversation(self):
        """Create sample Conversation entity."""
        conv = Conversation(user_id="user-123")
        # Manually set status as enum object
        object.__setattr__(conv, "status", ConversationStatus.ACTIVE)
        return conv

    @pytest.fixture
    def sample_conversation_orm(self, sample_conversation):
        """Create sample ConversationORM."""
        return ConversationORM(
            id=sample_conversation.id,
            user_id=sample_conversation.user_id,
            status="active",
            metadata={},
            agent_state={},
            started_at=sample_conversation.started_at,
            ended_at=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    @pytest.fixture
    def sample_message_orm(self):
        """Create sample MessageORM."""
        return MessageORM(
            id=uuid4(),
            conversation_id=uuid4(),
            role="user",
            content="Hello, I want to send money",
            message_metadata={},
            timestamp=datetime.utcnow(),
        )

    @pytest.mark.asyncio
    async def test_repository_initialization(self, mock_session):
        """Test repository initializes with session."""
        repo = ConversationRepository(mock_session)
        assert repo.session == mock_session

    @pytest.mark.asyncio
    async def test_create_conversation(
        self, mock_session, sample_conversation, sample_conversation_orm
    ):
        """Test creating a new conversation."""
        repo = ConversationRepository(mock_session)

        async def refresh_side_effect(orm):
            # Simulate database setting updated_at after flush/refresh
            orm.updated_at = datetime.utcnow()

        mock_session.refresh.side_effect = refresh_side_effect

        result = await repo.create(sample_conversation)

        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()

        assert isinstance(result, Conversation)
        assert result.user_id == "user-123"

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, mock_session, sample_conversation_orm):
        """Test getting conversation by ID when found."""
        repo = ConversationRepository(mock_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_conversation_orm
        mock_session.execute.return_value = mock_result

        conversation = await repo.get_by_id(sample_conversation_orm.id)

        assert conversation is not None
        assert conversation.id == sample_conversation_orm.id
        assert conversation.user_id == sample_conversation_orm.user_id
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, mock_session):
        """Test getting conversation by ID when not found."""
        repo = ConversationRepository(mock_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        conversation = await repo.get_by_id(uuid4())

        assert conversation is None
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_user_id(self, mock_session, sample_conversation_orm):
        """Test getting conversations by user ID."""
        repo = ConversationRepository(mock_session)

        orm_list = [sample_conversation_orm]
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = orm_list
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        conversations = await repo.get_by_user_id("user-123", limit=10, offset=0)

        assert len(conversations) == 1
        assert conversations[0].user_id == "user-123"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_active_conversation_found(self, mock_session, sample_conversation_orm):
        """Test getting active conversation when one exists."""
        repo = ConversationRepository(mock_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_conversation_orm
        mock_session.execute.return_value = mock_result

        conversation = await repo.get_active_conversation("user-123")

        assert conversation is not None
        assert conversation.user_id == "user-123"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_active_conversation_not_found(self, mock_session):
        """Test getting active conversation when none exists."""
        repo = ConversationRepository(mock_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        conversation = await repo.get_active_conversation("user-456")

        assert conversation is None
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_conversation(
        self, mock_session, sample_conversation, sample_conversation_orm
    ):
        """Test updating an existing conversation."""
        repo = ConversationRepository(mock_session)

        sample_conversation.complete()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_conversation_orm
        mock_session.execute.return_value = mock_result

        updated = await repo.update(sample_conversation)

        assert isinstance(updated, Conversation)
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_conversation_not_found(self, mock_session, sample_conversation):
        """Test updating conversation that doesn't exist."""
        repo = ConversationRepository(mock_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        with pytest.raises(ValueError) as exc_info:
            await repo.update(sample_conversation)

        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_status(self, mock_session, sample_conversation_orm):
        """Test updating conversation status."""
        repo = ConversationRepository(mock_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_conversation_orm
        mock_session.execute.return_value = mock_result

        updated = await repo.update_status(sample_conversation_orm.id, ConversationStatus.COMPLETED)

        assert isinstance(updated, Conversation)
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_status_not_found(self, mock_session):
        """Test updating status of non-existent conversation."""
        repo = ConversationRepository(mock_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        with pytest.raises(ValueError) as exc_info:
            await repo.update_status(uuid4(), ConversationStatus.COMPLETED)

        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_agent_state(self, mock_session, sample_conversation_orm):
        """Test updating agent state."""
        repo = ConversationRepository(mock_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_conversation_orm
        mock_session.execute.return_value = mock_result

        new_state = {"step": "confirming", "attempts": 1}
        updated = await repo.update_agent_state(sample_conversation_orm.id, new_state)

        assert isinstance(updated, Conversation)
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_agent_state_not_found(self, mock_session):
        """Test updating agent state of non-existent conversation."""
        repo = ConversationRepository(mock_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        with pytest.raises(ValueError) as exc_info:
            await repo.update_agent_state(uuid4(), {})

        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_add_message(self, mock_session, sample_conversation_orm):
        """Test adding a message to conversation."""
        repo = ConversationRepository(mock_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_conversation_orm
        mock_session.execute.return_value = mock_result

        async def refresh_side_effect(orm):
            # Simulate database generating ID for MessageORM
            if not orm.id:
                orm.id = uuid4()

        mock_session.refresh.side_effect = refresh_side_effect

        result = await repo.add_message(
            sample_conversation_orm.id, MessageRole.USER, "Hello, I want to send money"
        )

        assert isinstance(result, Message)
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_message_with_metadata(self, mock_session, sample_conversation_orm):
        """Test adding message with metadata."""
        repo = ConversationRepository(mock_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_conversation_orm
        mock_session.execute.return_value = mock_result

        async def refresh_side_effect(orm):
            # Simulate database generating ID for MessageORM
            if not orm.id:
                orm.id = uuid4()

        mock_session.refresh.side_effect = refresh_side_effect

        result = await repo.add_message(
            sample_conversation_orm.id,
            MessageRole.ASSISTANT,
            "Sure, I can help with that",
            metadata={"intent": "transfer"},
        )

        assert isinstance(result, Message)
        mock_session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_message_conversation_not_found(self, mock_session):
        """Test adding message to non-existent conversation."""
        repo = ConversationRepository(mock_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        with pytest.raises(ValueError) as exc_info:
            await repo.add_message(uuid4(), MessageRole.USER, "Hello")

        assert "Conversation" in str(exc_info.value)
        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_messages(self, mock_session, sample_message_orm):
        """Test getting messages for a conversation."""
        repo = ConversationRepository(mock_session)

        orm_list = [sample_message_orm]
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = orm_list
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        messages = await repo.get_messages(sample_message_orm.conversation_id)

        assert len(messages) == 1
        assert messages[0].conversation_id == sample_message_orm.conversation_id
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_messages_with_limit(self, mock_session, sample_message_orm):
        """Test getting messages with limit."""
        repo = ConversationRepository(mock_session)

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        messages = await repo.get_messages(sample_message_orm.conversation_id, limit=5)

        assert len(messages) == 0
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_last_message_found(self, mock_session, sample_message_orm):
        """Test getting last message when it exists."""
        repo = ConversationRepository(mock_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_message_orm
        mock_session.execute.return_value = mock_result

        message = await repo.get_last_message(sample_message_orm.conversation_id)

        assert message is not None
        assert isinstance(message, Message)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_last_message_not_found(self, mock_session):
        """Test getting last message when conversation is empty."""
        repo = ConversationRepository(mock_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        message = await repo.get_last_message(uuid4())

        assert message is None
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_conversation_found(self, mock_session, sample_conversation_orm):
        """Test deleting an existing conversation."""
        repo = ConversationRepository(mock_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_conversation_orm
        mock_session.execute.return_value = mock_result

        deleted = await repo.delete(sample_conversation_orm.id)

        assert deleted is True
        mock_session.delete.assert_called_once_with(sample_conversation_orm)
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_conversation_not_found(self, mock_session):
        """Test deleting a non-existent conversation."""
        repo = ConversationRepository(mock_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        deleted = await repo.delete(uuid4())

        assert deleted is False
        mock_session.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_to_entity_conversion(self, mock_session, sample_conversation_orm):
        """Test ORM to Entity conversion."""
        repo = ConversationRepository(mock_session)

        entity = repo._to_entity(sample_conversation_orm)

        assert isinstance(entity, Conversation)
        assert entity.id == sample_conversation_orm.id
        assert entity.user_id == sample_conversation_orm.user_id
        assert entity.status == ConversationStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_message_to_entity_conversion(self, mock_session, sample_message_orm):
        """Test MessageORM to Message entity conversion."""
        repo = ConversationRepository(mock_session)

        entity = repo._message_to_entity(sample_message_orm)

        assert isinstance(entity, Message)
        assert entity.id == sample_message_orm.id
        assert entity.conversation_id == sample_message_orm.conversation_id
        assert entity.role == MessageRole.USER
        assert entity.content == sample_message_orm.content
