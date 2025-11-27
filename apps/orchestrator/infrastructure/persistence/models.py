"""SQLAlchemy ORM models for persistence layer.

These models map to database tables and are separate from domain models.
Following the separation of concerns principle, these are pure data models
without business logic.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    UUID as SQLAlchemyUUID,  # noqa: N811
)
from sqlalchemy import (
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from apps.orchestrator.domain.entities import (
    ConversationStatus,
    MessageRole,
    TransactionStatus,
)


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


class ConversationORM(Base):
    """Conversation table - stores chat session data.

    Maps to domain.entities.Conversation
    """

    __tablename__ = "conversations"

    # Primary key using UUID
    id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    # User identification
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Status
    status: Mapped[str] = mapped_column(
        Enum(ConversationStatus, native_enum=False, length=20),
        nullable=False,
        default=ConversationStatus.ACTIVE.value,
        index=True,
    )

    # Timestamps
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # LangGraph agent state stored as JSON
    agent_state: Mapped[dict[str, Any] | None] = mapped_column(
        Text,  # Store as JSON text for PostgreSQL compatibility
        nullable=True,
    )

    # Audit timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,  # For sorting and filtering
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    messages: Mapped[list["MessageORM"]] = relationship(
        "MessageORM",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="MessageORM.timestamp",
    )
    transactions: Mapped[list["TransactionORM"]] = relationship(
        "TransactionORM",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )

    # Composite indexes for common queries
    __table_args__ = (
        Index("idx_conversations_user_status", "user_id", "status"),
        Index("idx_conversations_user_created", "user_id", "created_at"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Conversation(id={self.id}, user_id={self.user_id}, status={self.status})>"


class MessageORM(Base):
    """Message table - stores individual conversation messages.

    Maps to domain.entities.Message
    """

    __tablename__ = "messages"

    # Primary key using UUID
    id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    # Foreign key to conversation
    conversation_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Message content
    role: Mapped[str] = mapped_column(
        Enum(MessageRole, native_enum=False, length=20),
        nullable=False,
        index=True,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Additional structured data
    # Note: Using 'message_metadata' to avoid conflict with SQLAlchemy's 'metadata' attribute
    message_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",  # Column name in database
        Text,  # Store as JSON text
        nullable=True,
    )

    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,  # For chronological ordering
    )

    # Relationships
    conversation: Mapped["ConversationORM"] = relationship(
        "ConversationORM",
        back_populates="messages",
    )

    # Composite indexes for common queries
    __table_args__ = (
        Index("idx_messages_conversation_timestamp", "conversation_id", "timestamp"),
        Index("idx_messages_conversation_role", "conversation_id", "role"),
    )

    def __repr__(self) -> str:
        """String representation."""
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<Message(id={self.id}, role={self.role}, content='{content_preview}')>"


class TransactionORM(Base):
    """Transaction table - stores payment transaction data.

    Maps to domain.entities.Transaction
    """

    __tablename__ = "transactions"

    # Primary key using UUID
    id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    # Foreign key to conversation
    conversation_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # External transaction ID from payment service
    external_transaction_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
        index=True,
    )

    # User and recipient
    user_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    recipient_phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    # Transaction details
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="COP",
    )

    # Status tracking
    status: Mapped[str] = mapped_column(
        Enum(TransactionStatus, native_enum=False, length=20),
        nullable=False,
        default=TransactionStatus.PENDING.value,
        index=True,
    )
    validation_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,  # For sorting and filtering
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    conversation: Mapped["ConversationORM"] = relationship(
        "ConversationORM",
        back_populates="transactions",
    )

    # Composite indexes for common queries
    __table_args__ = (
        Index("idx_transactions_user_status", "user_id", "status"),
        Index("idx_transactions_user_created", "user_id", "created_at"),
        Index("idx_transactions_status_created", "status", "created_at"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<Transaction(id={self.id}, "
            f"external_id={self.external_transaction_id}, "
            f"status={self.status})>"
        )
