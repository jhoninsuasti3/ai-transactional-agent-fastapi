"""Conversation repository implementation.

Provides data access methods for Conversation and Message entities following
the Repository pattern for clean separation of concerns.
"""

import json
from datetime import datetime
from typing import Any, Sequence
from uuid import UUID

from sqlalchemy import Select, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from apps.orchestrator.domain.entities import (
    Conversation,
    ConversationStatus,
    Message,
    MessageRole,
)
from apps.orchestrator.infrastructure.persistence.models import ConversationORM, MessageORM


class ConversationRepository:
    """Repository for Conversation aggregate.

    Handles all data access operations for conversations and their messages
    with proper conversion between domain entities and ORM models.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create(self, conversation: Conversation) -> Conversation:
        """Create a new conversation.

        Args:
            conversation: Conversation entity to persist

        Returns:
            Conversation: Created conversation with database-generated fields

        Example:
            ```python
            conversation = Conversation(user_id="user123")
            saved = await repo.create(conversation)
            ```
        """
        orm_conversation = ConversationORM(
            id=conversation.id,
            user_id=conversation.user_id,
            status=conversation.status.value,
            started_at=conversation.started_at,
            ended_at=conversation.ended_at,
            agent_state=json.dumps(conversation.agent_state) if conversation.agent_state else None,
            created_at=conversation.created_at,
        )

        self.session.add(orm_conversation)
        await self.session.flush()
        await self.session.refresh(orm_conversation)

        return self._to_entity(orm_conversation)

    async def get_by_id(
        self,
        conversation_id: UUID,
        include_messages: bool = False,
    ) -> Conversation | None:
        """Get conversation by ID.

        Args:
            conversation_id: Conversation UUID
            include_messages: Whether to load messages (default False)

        Returns:
            Conversation entity or None if not found

        Example:
            ```python
            # Get conversation without messages
            conv = await repo.get_by_id(uuid4())

            # Get conversation with all messages
            conv = await repo.get_by_id(uuid4(), include_messages=True)
            ```
        """
        stmt = select(ConversationORM).where(ConversationORM.id == conversation_id)

        if include_messages:
            stmt = stmt.options(selectinload(ConversationORM.messages))

        result = await self.session.execute(stmt)
        orm_conversation = result.scalar_one_or_none()

        if not orm_conversation:
            return None

        return self._to_entity(orm_conversation, include_messages=include_messages)

    async def get_by_user_id(
        self,
        user_id: str,
        status: ConversationStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[Conversation]:
        """Get conversations for a user.

        Args:
            user_id: User identifier
            status: Optional status filter
            limit: Maximum number of results (default 50)
            offset: Number of results to skip (default 0)

        Returns:
            List of Conversation entities ordered by creation date (newest first)

        Example:
            ```python
            # Get all active conversations
            convs = await repo.get_by_user_id(
                "user123",
                status=ConversationStatus.ACTIVE,
            )
            ```
        """
        stmt: Select = select(ConversationORM).where(ConversationORM.user_id == user_id)

        if status:
            stmt = stmt.where(ConversationORM.status == status.value)

        stmt = stmt.order_by(desc(ConversationORM.created_at)).limit(limit).offset(offset)

        result = await self.session.execute(stmt)
        orm_conversations = result.scalars().all()

        return [self._to_entity(orm) for orm in orm_conversations]

    async def get_active_conversation(self, user_id: str) -> Conversation | None:
        """Get the active conversation for a user.

        Args:
            user_id: User identifier

        Returns:
            Active Conversation or None if no active conversation exists

        Example:
            ```python
            active_conv = await repo.get_active_conversation("user123")
            if not active_conv:
                # Create new conversation
                active_conv = await repo.create(Conversation(user_id="user123"))
            ```
        """
        stmt = (
            select(ConversationORM)
            .where(
                ConversationORM.user_id == user_id,
                ConversationORM.status == ConversationStatus.ACTIVE.value,
            )
            .order_by(desc(ConversationORM.created_at))
            .limit(1)
        )

        result = await self.session.execute(stmt)
        orm_conversation = result.scalar_one_or_none()

        return self._to_entity(orm_conversation) if orm_conversation else None

    async def update(self, conversation: Conversation) -> Conversation:
        """Update an existing conversation.

        Args:
            conversation: Conversation entity with updated values

        Returns:
            Updated conversation entity

        Raises:
            ValueError: If conversation not found

        Example:
            ```python
            conversation.complete()
            updated = await repo.update(conversation)
            ```
        """
        stmt = select(ConversationORM).where(ConversationORM.id == conversation.id)
        result = await self.session.execute(stmt)
        orm_conversation = result.scalar_one_or_none()

        if not orm_conversation:
            msg = f"Conversation {conversation.id} not found"
            raise ValueError(msg)

        # Update fields
        orm_conversation.status = conversation.status.value
        orm_conversation.ended_at = conversation.ended_at
        orm_conversation.agent_state = (
            json.dumps(conversation.agent_state) if conversation.agent_state else None
        )
        orm_conversation.updated_at = datetime.utcnow()

        await self.session.flush()
        await self.session.refresh(orm_conversation)

        return self._to_entity(orm_conversation)

    async def update_status(
        self,
        conversation_id: UUID,
        status: ConversationStatus,
    ) -> Conversation:
        """Update conversation status.

        Args:
            conversation_id: Conversation UUID
            status: New status

        Returns:
            Updated conversation entity

        Raises:
            ValueError: If conversation not found

        Example:
            ```python
            conversation = await repo.update_status(
                conv_id,
                ConversationStatus.COMPLETED,
            )
            ```
        """
        stmt = select(ConversationORM).where(ConversationORM.id == conversation_id)
        result = await self.session.execute(stmt)
        orm_conversation = result.scalar_one_or_none()

        if not orm_conversation:
            msg = f"Conversation {conversation_id} not found"
            raise ValueError(msg)

        orm_conversation.status = status.value
        orm_conversation.updated_at = datetime.utcnow()

        if status in {ConversationStatus.COMPLETED, ConversationStatus.ABANDONED}:
            orm_conversation.ended_at = datetime.utcnow()

        await self.session.flush()
        await self.session.refresh(orm_conversation)

        return self._to_entity(orm_conversation)

    async def update_agent_state(
        self,
        conversation_id: UUID,
        agent_state: dict[str, Any],
    ) -> Conversation:
        """Update the LangGraph agent state.

        Args:
            conversation_id: Conversation UUID
            agent_state: New agent state dictionary

        Returns:
            Updated conversation entity

        Raises:
            ValueError: If conversation not found

        Example:
            ```python
            state = {"step": "collecting_phone", "attempts": 1}
            conversation = await repo.update_agent_state(conv_id, state)
            ```
        """
        stmt = select(ConversationORM).where(ConversationORM.id == conversation_id)
        result = await self.session.execute(stmt)
        orm_conversation = result.scalar_one_or_none()

        if not orm_conversation:
            msg = f"Conversation {conversation_id} not found"
            raise ValueError(msg)

        orm_conversation.agent_state = json.dumps(agent_state)
        orm_conversation.updated_at = datetime.utcnow()

        await self.session.flush()
        await self.session.refresh(orm_conversation)

        return self._to_entity(orm_conversation)

    # Message operations

    async def add_message(
        self,
        conversation_id: UUID,
        role: MessageRole,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> Message:
        """Add a message to a conversation.

        Args:
            conversation_id: Conversation UUID
            role: Message sender role
            content: Message text content
            metadata: Optional metadata dictionary

        Returns:
            Created Message entity

        Raises:
            ValueError: If conversation not found

        Example:
            ```python
            message = await repo.add_message(
                conv_id,
                MessageRole.USER,
                "I want to transfer money",
                metadata={"intent": "transfer"},
            )
            ```
        """
        # Verify conversation exists
        stmt = select(ConversationORM).where(ConversationORM.id == conversation_id)
        result = await self.session.execute(stmt)
        conversation = result.scalar_one_or_none()

        if not conversation:
            msg = f"Conversation {conversation_id} not found"
            raise ValueError(msg)

        # Create message
        orm_message = MessageORM(
            conversation_id=conversation_id,
            role=role.value,
            content=content,
            message_metadata=json.dumps(metadata) if metadata else None,
            timestamp=datetime.utcnow(),
        )

        self.session.add(orm_message)

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()

        await self.session.flush()
        await self.session.refresh(orm_message)

        return self._message_to_entity(orm_message)

    async def get_messages(
        self,
        conversation_id: UUID,
        role: MessageRole | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Message]:
        """Get messages for a conversation.

        Args:
            conversation_id: Conversation UUID
            role: Optional role filter
            limit: Maximum number of results (default 100)
            offset: Number of results to skip (default 0)

        Returns:
            List of Message entities in chronological order

        Example:
            ```python
            # Get all messages
            messages = await repo.get_messages(conv_id)

            # Get only user messages
            user_messages = await repo.get_messages(
                conv_id,
                role=MessageRole.USER,
            )
            ```
        """
        stmt: Select = select(MessageORM).where(MessageORM.conversation_id == conversation_id)

        if role:
            stmt = stmt.where(MessageORM.role == role.value)

        stmt = stmt.order_by(MessageORM.timestamp).limit(limit).offset(offset)

        result = await self.session.execute(stmt)
        orm_messages = result.scalars().all()

        return [self._message_to_entity(orm) for orm in orm_messages]

    async def get_last_message(self, conversation_id: UUID) -> Message | None:
        """Get the most recent message in a conversation.

        Args:
            conversation_id: Conversation UUID

        Returns:
            Most recent Message or None if no messages

        Example:
            ```python
            last_msg = await repo.get_last_message(conv_id)
            if last_msg and last_msg.is_from_user():
                # Process user message
                pass
            ```
        """
        stmt = (
            select(MessageORM)
            .where(MessageORM.conversation_id == conversation_id)
            .order_by(desc(MessageORM.timestamp))
            .limit(1)
        )

        result = await self.session.execute(stmt)
        orm_message = result.scalar_one_or_none()

        return self._message_to_entity(orm_message) if orm_message else None

    async def delete(self, conversation_id: UUID) -> bool:
        """Delete a conversation and all its messages.

        Args:
            conversation_id: Conversation UUID

        Returns:
            True if deleted, False if not found

        Note:
            Messages are automatically deleted via CASCADE

        Example:
            ```python
            deleted = await repo.delete(conv_id)
            ```
        """
        stmt = select(ConversationORM).where(ConversationORM.id == conversation_id)
        result = await self.session.execute(stmt)
        orm_conversation = result.scalar_one_or_none()

        if not orm_conversation:
            return False

        await self.session.delete(orm_conversation)
        await self.session.flush()

        return True

    # Private helper methods

    def _to_entity(
        self,
        orm: ConversationORM,
        include_messages: bool = False,
    ) -> Conversation:
        """Convert ORM model to domain entity.

        Args:
            orm: ConversationORM instance
            include_messages: Whether to include messages

        Returns:
            Conversation domain entity
        """
        agent_state = json.loads(orm.agent_state) if orm.agent_state else None

        conversation = Conversation(
            id=orm.id,
            user_id=orm.user_id,
            status=ConversationStatus(orm.status),
            agent_state=agent_state,
            started_at=orm.started_at,
            ended_at=orm.ended_at,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

        # Load messages if requested and available
        if include_messages and hasattr(orm, "messages") and orm.messages:
            conversation.messages = [self._message_to_entity(msg) for msg in orm.messages]

        return conversation

    def _message_to_entity(self, orm: MessageORM) -> Message:
        """Convert MessageORM to Message entity.

        Args:
            orm: MessageORM instance

        Returns:
            Message domain entity
        """
        metadata = json.loads(orm.message_metadata) if orm.message_metadata else {}

        return Message(
            id=orm.id,
            conversation_id=orm.conversation_id,
            role=MessageRole(orm.role),
            content=orm.content,
            metadata=metadata,
            timestamp=orm.timestamp,
        )