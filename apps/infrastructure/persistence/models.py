"""SQLAlchemy ORM models for persistence layer.

These models map to database tables and are separate from domain models.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Enum, Float, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from apps.domain.models import ConversationStatus, TransactionStatus


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


class ConversationORM(Base):
    """Conversation table - stores chat session data.

    Maps to domain.models.Conversation
    """

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        Enum(ConversationStatus, native_enum=False, length=20),
        nullable=False,
        default=ConversationStatus.ACTIVE,
        index=True,
    )
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
        JSON,
        nullable=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Conversation(id={self.id}, user_id={self.user_id}, status={self.status})>"


class TransactionORM(Base):
    """Transaction table - stores payment transaction data.

    Maps to domain.models.Transaction
    """

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    # External transaction ID from payment service
    transaction_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
        index=True,
    )

    # Transaction details
    recipient_phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )
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
        default=TransactionStatus.PENDING,
        index=True,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Transaction(id={self.id}, transaction_id={self.transaction_id}, status={self.status})>"