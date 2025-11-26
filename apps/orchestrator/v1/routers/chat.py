# -*- coding: utf-8 -*-
"""Chat router for API v1 - Integrated with LangGraph agent."""

import uuid
from typing import Dict, Any

import structlog
from fastapi import APIRouter, HTTPException
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import HumanMessage

from apps.orchestrator.v1.schemas import ChatRequest, ChatResponse
from apps.agents.transactional.graph import get_agent
from apps.agents.transactional.state import TransactionalState
from apps.orchestrator.settings import settings
from apps.orchestrator.constants import LANGGRAPH_RECURSION_LIMIT

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


def _create_checkpointer() -> PostgresSaver:
    """Create PostgreSQL checkpointer for conversation persistence.

    Returns the context manager - it will be used with .__ enter__() when compiling the graph.
    """
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
        # TEMPORARILY DISABLED: PostgreSQL checkpointing
        # TODO: Fix PostgreSQL connection issues
        # Get agent without checkpointer for now
        agent = get_agent(checkpointer=None)

        # Prepare input with only the new message
        input_data = {
            "messages": [HumanMessage(content=request.message)],
        }

        # Run agent with config
        config = {
            "configurable": {
                "thread_id": conversation_id,
            },
            "recursion_limit": LANGGRAPH_RECURSION_LIMIT,
        }

        # Invoke agent (without checkpointer, state won't persist)
        result = agent.invoke(input_data, config=config)

        # Extract response from agent state (LangChain message objects)
        messages = result.get("messages", [])
        last_message = messages[-1] if messages else None

        # Extract text from message content (handle both string and list formats)
        if last_message:
            content = last_message.content
            if isinstance(content, list):
                # Extract text parts from content blocks
                text_parts = [
                    block.get("text", "") if isinstance(block, dict) else str(block)
                    for block in content
                    if isinstance(block, dict) and block.get("type") == "text"
                ]
                response_text = " ".join(text_parts) if text_parts else "Lo siento, hubo un error."
            elif isinstance(content, str):
                response_text = content
            else:
                response_text = str(content)
        else:
            response_text = "Lo siento, hubo un error."

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