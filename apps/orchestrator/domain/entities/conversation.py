"""Conversation domain entity and aggregate root.

A conversation represents a complete user session with the agent, including
all messages and associated transactions.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from apps.orchestrator.domain.entities.message import Message


class ConversationStatus(str, Enum):
    """Conversation lifecycle status."""

    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class Conversation(BaseModel):
    """Conversation aggregate root.

    Manages the complete lifecycle of a user conversation including messages,
    state, and business rules.

    Attributes:
        id: Unique conversation identifier
        user_id: User who owns this conversation
        status: Current conversation status
        messages: List of messages in chronological order
        transaction_ids: List of transaction IDs created in this conversation
        agent_state: LangGraph state snapshot for resuming
        started_at: When conversation began
        ended_at: When conversation ended
        created_at: Database creation timestamp
        updated_at: Database update timestamp
    """

    model_config = {"from_attributes": True, "use_enum_values": True}

    # Identity
    id: UUID = Field(default_factory=uuid4, description="Unique conversation ID")
    user_id: str = Field(..., min_length=1, description="User identifier")

    # Status
    status: ConversationStatus = Field(
        default=ConversationStatus.ACTIVE,
        description="Conversation status",
    )

    # Related data
    messages: list[Message] = Field(
        default_factory=list,
        description="Conversation messages",
    )
    transaction_ids: list[UUID] = Field(
        default_factory=list,
        description="Associated transaction IDs",
    )

    # LangGraph state (for resuming conversations)
    agent_state: dict[str, Any] | None = Field(
        None,
        description="LangGraph agent state snapshot",
    )

    # Timestamps
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Conversation start time",
    )
    ended_at: datetime | None = Field(None, description="Conversation end time")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Database creation time",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Database update time",
    )

    # Business logic methods

    def add_message(self, message: Message) -> None:
        """Add a message to the conversation.

        Args:
            message: Message to add

        Raises:
            ValueError: If conversation is not active
        """
        if not self.is_active():
            msg = "Cannot add message to inactive conversation"
            raise ValueError(msg)

        if message.conversation_id != self.id:
            msg = "Message conversation_id does not match"
            raise ValueError(msg)

        self.messages.append(message)
        self.updated_at = datetime.now(UTC)

    def add_transaction_id(self, transaction_id: UUID) -> None:
        """Associate a transaction with this conversation.

        Args:
            transaction_id: Transaction UUID to associate
        """
        if transaction_id not in self.transaction_ids:
            self.transaction_ids.append(transaction_id)
            self.updated_at = datetime.now(UTC)

    def complete(self, ended_at: datetime | None = None) -> None:
        """Mark conversation as completed successfully.

        Args:
            ended_at: End timestamp (defaults to now)

        Raises:
            ValueError: If conversation is not active
        """
        if not self.is_active():
            msg = "Conversation is not active"
            raise ValueError(msg)

        self.status = ConversationStatus.COMPLETED
        self.ended_at = ended_at or datetime.now(UTC)
        self.updated_at = datetime.now(UTC)

    def abandon(self, ended_at: datetime | None = None) -> None:
        """Mark conversation as abandoned (user left without completing).

        Args:
            ended_at: End timestamp (defaults to now)
        """
        if not self.is_active():
            msg = "Conversation is not active"
            raise ValueError(msg)

        self.status = ConversationStatus.ABANDONED
        self.ended_at = ended_at or datetime.now(UTC)
        self.updated_at = datetime.now(UTC)

    def update_agent_state(self, state: dict[str, Any]) -> None:
        """Update the LangGraph agent state.

        Args:
            state: New state dictionary
        """
        self.agent_state = state
        self.updated_at = datetime.now(UTC)

    def is_active(self) -> bool:
        """Check if conversation is active."""
        return self.status == ConversationStatus.ACTIVE

    def is_completed(self) -> bool:
        """Check if conversation is completed."""
        return self.status == ConversationStatus.COMPLETED

    def is_abandoned(self) -> bool:
        """Check if conversation is abandoned."""
        return self.status == ConversationStatus.ABANDONED

    def is_ended(self) -> bool:
        """Check if conversation has ended (completed or abandoned)."""
        return self.status in {
            ConversationStatus.COMPLETED,
            ConversationStatus.ABANDONED,
        }

    def get_last_message(self) -> Message | None:
        """Get the most recent message.

        Returns:
            Last message or None if no messages
        """
        return self.messages[-1] if self.messages else None

    def get_user_messages(self) -> list[Message]:
        """Get all messages from the user.

        Returns:
            List of user messages
        """
        return [msg for msg in self.messages if msg.is_from_user()]

    def get_assistant_messages(self) -> list[Message]:
        """Get all messages from the assistant.

        Returns:
            List of assistant messages
        """
        return [msg for msg in self.messages if msg.is_from_assistant()]

    def message_count(self) -> int:
        """Get total number of messages.

        Returns:
            Message count
        """
        return len(self.messages)

    def duration_seconds(self) -> float | None:
        """Calculate conversation duration in seconds.

        Returns:
            Duration in seconds or None if not ended
        """
        if not self.ended_at:
            return None

        return (self.ended_at - self.started_at).total_seconds()

    def __str__(self) -> str:
        """String representation."""
        return (
            f"Conversation(id={self.id}, "
            f"user={self.user_id}, "
            f"status={self.status.value}, "
            f"messages={self.message_count()})"
        )
