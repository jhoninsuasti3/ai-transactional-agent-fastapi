"""Message domain entity for conversation history.

Messages represent individual exchanges in a conversation between user and agent.
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Message sender role."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    """Message entity representing a single conversation exchange.

    Each message is part of a conversation and represents one turn in the dialogue.

    Attributes:
        id: Unique message identifier
        conversation_id: Parent conversation ID
        role: Who sent the message (user, assistant, system)
        content: Message text content
        metadata: Additional structured data (JSON)
        timestamp: When message was created
    """

    model_config = {"from_attributes": True, "use_enum_values": True}

    # Identity
    id: UUID = Field(default_factory=uuid4, description="Unique message ID")
    conversation_id: UUID = Field(..., description="Parent conversation ID")

    # Content
    role: MessageRole = Field(..., description="Message sender role")
    content: str = Field(..., min_length=1, description="Message content")

    # Additional data
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (intent, confidence, etc.)",
    )

    # Timestamp
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Message creation time",
    )

    # Business logic methods

    def is_from_user(self) -> bool:
        """Check if message is from user."""
        return self.role == MessageRole.USER

    def is_from_assistant(self) -> bool:
        """Check if message is from assistant."""
        return self.role == MessageRole.ASSISTANT

    def is_system_message(self) -> bool:
        """Check if message is a system message."""
        return self.role == MessageRole.SYSTEM

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata key-value pair.

        Args:
            key: Metadata key
            value: Metadata value (must be JSON-serializable)
        """
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value by key.

        Args:
            key: Metadata key
            default: Default value if key not found

        Returns:
            Metadata value or default
        """
        return self.metadata.get(key, default)

    def excerpt(self, max_length: int = 50) -> str:
        """Get truncated content for display.

        Args:
            max_length: Maximum length of excerpt

        Returns:
            Truncated content with ellipsis if needed
        """
        if len(self.content) <= max_length:
            return self.content

        return f"{self.content[: max_length - 3]}..."

    def __str__(self) -> str:
        """String representation."""
        return f"Message({self.role.value}: {self.excerpt()})"
