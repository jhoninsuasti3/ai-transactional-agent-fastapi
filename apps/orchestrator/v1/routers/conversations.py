"""Conversations router for API v1."""

from datetime import UTC, datetime

from fastapi import APIRouter

from apps.orchestrator.v1.schemas import (
    ConversationDetail,
    ConversationStatus,
    Message,
    MessageRole,
)

router = APIRouter(prefix="/conversations", tags=["conversations"])
conversations_store: dict[str, dict] = {}


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(conversation_id: str) -> ConversationDetail:
    """Get conversation details by ID."""
    if conversation_id not in conversations_store:
        return ConversationDetail(
            conversation_id=conversation_id,
            user_id="user-123",
            status=ConversationStatus.ACTIVE,
            messages=[
                Message(role=MessageRole.USER, content="Hola", timestamp=datetime.now(UTC)),
                Message(
                    role=MessageRole.ASSISTANT,
                    content="Hola! Como puedo ayudarte?",
                    timestamp=datetime.now(UTC),
                ),
            ],
            started_at=datetime.now(UTC),
            ended_at=None,
            transaction_ids=[],
        )
    return ConversationDetail(**conversations_store[conversation_id])


@router.get("/health")
async def conversations_health():
    """Health check for conversations router."""
    return {"status": "healthy", "router": "conversations", "version": "v1"}
