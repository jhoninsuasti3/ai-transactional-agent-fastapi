"""Repository implementations for data persistence.

These implement the port interfaces defined in domain.ports
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.apps.core.exceptions import NotFoundError
from apps.apps.domain.models import Conversation, ConversationStatus, Transaction
from apps.apps.domain.ports.repository_port import (
    ConversationRepository,
    TransactionRepository,
)
from apps.apps.infrastructure.persistence.models import ConversationORM, TransactionORM


class ConversationRepositoryImpl(ConversationRepository):
    """SQLAlchemy implementation of ConversationRepository."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create(self, conversation: Conversation) -> Conversation:
        """Create a new conversation.

        Args:
            conversation: Conversation entity to create

        Returns:
            Created conversation with assigned ID
        """
        orm_model = ConversationORM(
            user_id=conversation.user_id,
            status=conversation.status,
            agent_state=conversation.agent_state,
        )

        self.session.add(orm_model)
        await self.session.flush()  # Get ID without committing
        await self.session.refresh(orm_model)

        return self._to_domain(orm_model)

    async def get_by_id(self, conversation_id: int) -> Conversation | None:
        """Get conversation by ID.

        Args:
            conversation_id: Conversation ID

        Returns:
            Conversation if found, None otherwise
        """
        result = await self.session.execute(
            select(ConversationORM).where(ConversationORM.id == conversation_id)
        )
        orm_model = result.scalar_one_or_none()

        if orm_model is None:
            return None

        return self._to_domain(orm_model)

    async def get_by_user_id(self, user_id: str) -> list[Conversation]:
        """Get all conversations for a user.

        Args:
            user_id: User identifier

        Returns:
            List of conversations (may be empty)
        """
        result = await self.session.execute(
            select(ConversationORM)
            .where(ConversationORM.user_id == user_id)
            .order_by(ConversationORM.created_at.desc())
        )
        orm_models = result.scalars().all()

        return [self._to_domain(model) for model in orm_models]

    async def update_status(
        self,
        conversation_id: int,
        status: ConversationStatus,
    ) -> Conversation:
        """Update conversation status.

        Args:
            conversation_id: Conversation ID
            status: New status

        Returns:
            Updated conversation

        Raises:
            NotFoundError: Conversation not found
        """
        result = await self.session.execute(
            select(ConversationORM).where(ConversationORM.id == conversation_id)
        )
        orm_model = result.scalar_one_or_none()

        if orm_model is None:
            raise NotFoundError("Conversation", conversation_id)

        orm_model.status = status
        await self.session.flush()
        await self.session.refresh(orm_model)

        return self._to_domain(orm_model)

    async def update_agent_state(
        self,
        conversation_id: int,
        agent_state: dict[str, Any],
    ) -> Conversation:
        """Update LangGraph agent state.

        Args:
            conversation_id: Conversation ID
            agent_state: New agent state snapshot

        Returns:
            Updated conversation

        Raises:
            NotFoundError: Conversation not found
        """
        result = await self.session.execute(
            select(ConversationORM).where(ConversationORM.id == conversation_id)
        )
        orm_model = result.scalar_one_or_none()

        if orm_model is None:
            raise NotFoundError("Conversation", conversation_id)

        orm_model.agent_state = agent_state
        await self.session.flush()
        await self.session.refresh(orm_model)

        return self._to_domain(orm_model)

    async def delete(self, conversation_id: int) -> None:
        """Delete a conversation.

        Args:
            conversation_id: Conversation ID

        Raises:
            NotFoundError: Conversation not found
        """
        result = await self.session.execute(
            select(ConversationORM).where(ConversationORM.id == conversation_id)
        )
        orm_model = result.scalar_one_or_none()

        if orm_model is None:
            raise NotFoundError("Conversation", conversation_id)

        await self.session.delete(orm_model)
        await self.session.flush()

    @staticmethod
    def _to_domain(orm_model: ConversationORM) -> Conversation:
        """Convert ORM model to domain model.

        Args:
            orm_model: SQLAlchemy ORM model

        Returns:
            Domain model
        """
        return Conversation(
            id=orm_model.id,
            user_id=orm_model.user_id,
            status=ConversationStatus(orm_model.status),
            started_at=orm_model.started_at,
            ended_at=orm_model.ended_at,
            agent_state=orm_model.agent_state,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )


class TransactionRepositoryImpl(TransactionRepository):
    """SQLAlchemy implementation of TransactionRepository."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create(self, transaction: Transaction) -> Transaction:
        """Create a new transaction.

        Args:
            transaction: Transaction entity to create

        Returns:
            Created transaction with assigned ID
        """
        orm_model = TransactionORM(
            conversation_id=transaction.conversation_id,
            transaction_id=transaction.transaction_id,
            recipient_phone=transaction.recipient_phone,
            amount=transaction.amount,
            currency=transaction.currency,
            status=transaction.status,
            error_message=transaction.error_message,
        )

        self.session.add(orm_model)
        await self.session.flush()
        await self.session.refresh(orm_model)

        return self._to_domain(orm_model)

    async def get_by_id(self, transaction_id: int) -> Transaction | None:
        """Get transaction by database ID.

        Args:
            transaction_id: Database transaction ID

        Returns:
            Transaction if found, None otherwise
        """
        result = await self.session.execute(
            select(TransactionORM).where(TransactionORM.id == transaction_id)
        )
        orm_model = result.scalar_one_or_none()

        if orm_model is None:
            return None

        return self._to_domain(orm_model)

    async def get_by_external_id(
        self,
        external_transaction_id: str,
    ) -> Transaction | None:
        """Get transaction by external service ID.

        Args:
            external_transaction_id: Transaction ID from external service

        Returns:
            Transaction if found, None otherwise
        """
        result = await self.session.execute(
            select(TransactionORM).where(
                TransactionORM.transaction_id == external_transaction_id
            )
        )
        orm_model = result.scalar_one_or_none()

        if orm_model is None:
            return None

        return self._to_domain(orm_model)

    async def get_by_conversation_id(
        self,
        conversation_id: int,
    ) -> list[Transaction]:
        """Get all transactions for a conversation.

        Args:
            conversation_id: Conversation ID

        Returns:
            List of transactions (may be empty)
        """
        result = await self.session.execute(
            select(TransactionORM)
            .where(TransactionORM.conversation_id == conversation_id)
            .order_by(TransactionORM.created_at.desc())
        )
        orm_models = result.scalars().all()

        return [self._to_domain(model) for model in orm_models]

    async def update_status(
        self,
        transaction_id: int,
        status: str,
        error_message: str | None = None,
    ) -> Transaction:
        """Update transaction status.

        Args:
            transaction_id: Database transaction ID
            status: New status
            error_message: Error message if failed

        Returns:
            Updated transaction

        Raises:
            NotFoundError: Transaction not found
        """
        result = await self.session.execute(
            select(TransactionORM).where(TransactionORM.id == transaction_id)
        )
        orm_model = result.scalar_one_or_none()

        if orm_model is None:
            raise NotFoundError("Transaction", transaction_id)

        orm_model.status = status
        if error_message:
            orm_model.error_message = error_message

        await self.session.flush()
        await self.session.refresh(orm_model)

        return self._to_domain(orm_model)

    async def delete(self, transaction_id: int) -> None:
        """Delete a transaction.

        Args:
            transaction_id: Database transaction ID

        Raises:
            NotFoundError: Transaction not found
        """
        result = await self.session.execute(
            select(TransactionORM).where(TransactionORM.id == transaction_id)
        )
        orm_model = result.scalar_one_or_none()

        if orm_model is None:
            raise NotFoundError("Transaction", transaction_id)

        await self.session.delete(orm_model)
        await self.session.flush()

    @staticmethod
    def _to_domain(orm_model: TransactionORM) -> Transaction:
        """Convert ORM model to domain model.

        Args:
            orm_model: SQLAlchemy ORM model

        Returns:
            Domain model
        """
        return Transaction(
            id=orm_model.id,
            conversation_id=orm_model.conversation_id,
            transaction_id=orm_model.transaction_id,
            recipient_phone=orm_model.recipient_phone,
            amount=orm_model.amount,
            currency=orm_model.currency,
            status=orm_model.status,
            error_message=orm_model.error_message,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )