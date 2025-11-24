# -*- coding: utf-8 -*-
"""Conversations router for API v1."""

from datetime import datetime
from fastapi import APIRouter
from apps.orchestrator.v1.schemas import ConversationDetail, ConversationStatus, Message, MessageRole

router = APIRouter(prefix="/conversations", tags=["conversations"])
conversations_store = {}


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(conversation_id: str) -> ConversationDetail:
    """Get conversation details by ID."""
    if conversation_id not in conversations_store:
        return ConversationDetail(
            conversation_id=conversation_id,
            user_id="user-123",
            status=ConversationStatus.ACTIVE,
            messages=[
                Message(role=MessageRole.USER, content="Hola", timestamp=datetime.utcnow()),
                Message(role=MessageRole.ASSISTANT, content="Hola! Como puedo ayudarte?", timestamp=datetime.utcnow()),
            ],
            started_at=datetime.utcnow(),
            ended_at=None,
            transaction_ids=[],
        )
    return ConversationDetail(**conversations_store[conversation_id])


@router.get("/health")
async def conversations_health():
    """Health check for conversations router."""
    return {"status": "healthy", "router": "conversations", "version": "v1"}