# -*- coding: utf-8 -*-
"""Chat router for API v1 - Integrated with LangGraph agent."""

import uuid
from typing import Dict, Any

import structlog
from fastapi import APIRouter, HTTPException
from langgraph.checkpoint.postgres import PostgresSaver

from apps.orchestrator.v1.schemas import ChatRequest, ChatResponse
from apps.agents.transactional.graph import agent
from apps.agents.transactional.state import TransactionalState
from apps.orchestrator.settings import settings

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


def _get_checkpointer() -> PostgresSaver:
    """Create PostgreSQL checkpointer for conversation persistence."""
    return PostgresSaver.from_conn_string(settings.LANGGRAPH_CHECKPOINT_DB)


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Chat endpoint with LangGraph agent integration.

    Args:
        request: Chat request with message and optional conversation_id

    Returns:
        ChatResponse with agent response and metadata
    """
    conversation_id = request.conversation_id or f"conv-{uuid.uuid4()}"

    logger.info(
        "chat_request_received",
        conversation_id=conversation_id,
        message=request.message,
    )

    try:
        # Prepare initial state
        initial_state: TransactionalState = {
            "messages": [{"role": "user", "content": request.message}],
            "phone": None,
            "amount": None,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
            "error": None,
        }

        # Create checkpointer for conversation persistence
        checkpointer = _get_checkpointer()

        # Run agent with checkpointing
        config = {
            "configurable": {
                "thread_id": conversation_id,
            }
        }

        # Invoke agent
        result = agent.invoke(
            initial_state,
            config=config,
            checkpointer=checkpointer,
        )

        # Extract response from agent state
        messages = result.get("messages", [])
        last_message = messages[-1] if messages else None
        response_text = last_message.get("content", "Lo siento, hubo un error.") if last_message else "Lo siento, hubo un error."

        # Build metadata from agent state
        metadata: Dict[str, Any] = {
            "phone": result.get("phone"),
            "amount": result.get("amount"),
            "needs_confirmation": result.get("needs_confirmation", False),
            "confirmed": result.get("confirmed", False),
            "transaction_status": result.get("transaction_status"),
        }

        # Remove None values from metadata
        metadata = {k: v for k, v in metadata.items() if v is not None}

        logger.info(
            "chat_response_generated",
            conversation_id=conversation_id,
            transaction_id=result.get("transaction_id"),
            status=result.get("transaction_status"),
        )

        return ChatResponse(
            response=response_text,
            conversation_id=conversation_id,
            transaction_id=result.get("transaction_id"),
            requires_confirmation=result.get("needs_confirmation", False),
            metadata=metadata,
        )

    except Exception as e:
        logger.error(
            "chat_error",
            conversation_id=conversation_id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )


@router.get("/health")
async def chat_health():
    """Health check for chat router."""
    return {
        "status": "healthy",
        "router": "chat",
        "version": "v1-langgraph",
        "agent_integrated": True,
        "langgraph_agent": "transactional",
    }