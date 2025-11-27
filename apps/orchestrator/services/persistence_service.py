"""Service for persisting conversation and transaction data to database.

This service handles saving data to the conversations, messages, and transactions
tables as required by the technical test requirements.
"""

import json
from datetime import UTC, datetime
from uuid import UUID, uuid4

import structlog
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from apps.orchestrator.infrastructure.persistence.models import (
    ConversationORM,
    MessageORM,
    TransactionORM,
)
from apps.orchestrator.settings import settings

logger = structlog.get_logger(__name__)


class PersistenceService:
    """Service to persist conversation and transaction data."""

    def __init__(self):
        """Initialize persistence service with sync database connection."""
        # Convert async URL to sync URL (replace postgresql+asyncpg with postgresql+psycopg)
        sync_url = settings.database_url_str.replace(
            "postgresql+asyncpg://", "postgresql+psycopg://"
        )
        self.engine = create_engine(sync_url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)

    def get_or_create_conversation(self, conversation_id: str, user_id: str) -> UUID:
        """Get existing conversation or create new one.

        Args:
            conversation_id: Thread ID from LangGraph
            user_id: User identifier

        Returns:
            UUID of conversation record
        """
        with self.SessionLocal() as session:
            # Parse conversation_id to UUID if it starts with "conv-"
            try:
                # Try to find by exact UUID match first
                conv_uuid = UUID(conversation_id.replace("conv-", ""))

                stmt = select(ConversationORM).where(ConversationORM.id == conv_uuid)
                conversation = session.execute(stmt).scalar_one_or_none()

                if conversation:
                    return conversation.id
            except ValueError:
                pass  # Not a valid UUID, will create new

            # Create new conversation
            conversation = ConversationORM(
                id=uuid4(),
                user_id=user_id,
                status="active",
                started_at=datetime.now(UTC),
            )
            session.add(conversation)
            session.commit()
            session.refresh(conversation)

            logger.info(
                "conversation_created",
                conversation_id=str(conversation.id),
                user_id=user_id,
            )

            return conversation.id

    def save_message(
        self,
        conversation_id: UUID,
        role: str,
        content: str,
        metadata: dict | None = None,
    ) -> UUID:
        """Save a message to the database.

        Args:
            conversation_id: UUID of conversation
            role: Message role (user/assistant)
            content: Message content
            metadata: Additional metadata

        Returns:
            UUID of message record
        """
        with self.SessionLocal() as session:
            message = MessageORM(
                conversation_id=conversation_id,
                role=role,
                content=content,
                message_metadata=json.dumps(metadata) if metadata else None,
                timestamp=datetime.now(UTC),
            )
            session.add(message)
            session.commit()
            session.refresh(message)

            logger.info(
                "message_saved",
                message_id=str(message.id),
                conversation_id=str(conversation_id),
                role=role,
            )

            return message.id

    def save_transaction(
        self,
        conversation_id: UUID,
        user_id: str,
        external_transaction_id: str,
        recipient_phone: str,
        amount: float,
        status: str = "completed",
        validation_id: str | None = None,
        error_message: str | None = None,
    ) -> UUID:
        """Save a transaction to the database.

        Args:
            conversation_id: UUID of conversation
            user_id: User identifier
            external_transaction_id: Transaction ID from external service
            recipient_phone: Recipient phone number
            amount: Transaction amount
            status: Transaction status
            validation_id: Validation ID if any
            error_message: Error message if failed

        Returns:
            UUID of transaction record
        """
        with self.SessionLocal() as session:
            transaction = TransactionORM(
                conversation_id=conversation_id,
                user_id=user_id,
                external_transaction_id=external_transaction_id,
                recipient_phone=recipient_phone,
                amount=amount,
                currency="COP",
                status=status,
                validation_id=validation_id,
                error_message=error_message,
                created_at=datetime.now(UTC),
                completed_at=datetime.now(UTC) if status == "completed" else None,
            )
            session.add(transaction)
            session.commit()
            session.refresh(transaction)

            logger.info(
                "transaction_saved",
                transaction_id=str(transaction.id),
                external_id=external_transaction_id,
                conversation_id=str(conversation_id),
                amount=amount,
                status=status,
            )

            return transaction.id

    def update_conversation_status(
        self, conversation_id: UUID, status: str, ended_at: datetime | None = None
    ) -> None:
        """Update conversation status.

        Args:
            conversation_id: UUID of conversation
            status: New status (active/completed/abandoned)
            ended_at: End timestamp if conversation ended
        """
        with self.SessionLocal() as session:
            stmt = select(ConversationORM).where(ConversationORM.id == conversation_id)
            conversation = session.execute(stmt).scalar_one_or_none()

            if conversation:
                conversation.status = status
                if ended_at:
                    conversation.ended_at = ended_at
                session.commit()

                logger.info(
                    "conversation_status_updated",
                    conversation_id=str(conversation_id),
                    status=status,
                )


# Global instance
persistence_service = PersistenceService()
