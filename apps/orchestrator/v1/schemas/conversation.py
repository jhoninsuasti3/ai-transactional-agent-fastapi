# -*- coding: utf-8 -*-
"""Conversation schemas for API v1."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ConversationStatus(str, Enum):
    """Conversation status states."""

    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class MessageRole(str, Enum):
    """Message role in conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    """Single message in a conversation."""

    role: MessageRole = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    metadata: dict | None = Field(None, description="Additional metadata")


class ConversationDetail(BaseModel):
    """Detailed conversation information."""

    conversation_id: str = Field(..., description="Unique conversation identifier")
    user_id: str = Field(..., description="User identifier")
    status: ConversationStatus = Field(..., description="Conversation status")
    messages: list[Message] = Field(..., description="List of messages")
    started_at: datetime = Field(..., description="Start timestamp")
    ended_at: datetime | None = Field(None, description="End timestamp")
    transaction_ids: list[str] = Field(default_factory=list, description="Transaction IDs")


class ConversationSummary(BaseModel):
    """Summary of a conversation."""

    conversation_id: str = Field(..., description="Unique conversation identifier")
    user_id: str = Field(..., description="User identifier")
    status: ConversationStatus = Field(..., description="Conversation status")
    message_count: int = Field(..., description="Number of messages")
    started_at: datetime = Field(..., description="Start timestamp")
    ended_at: datetime | None = Field(None, description="End timestamp")
    last_message: str | None = Field(None, description="Preview of last message")