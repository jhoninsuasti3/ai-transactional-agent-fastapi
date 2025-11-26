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
from apps.orchestrator.services.persistence_service import persistence_service

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
        # Create checkpointer context manager
        checkpointer_cm = _create_checkpointer()

        # Use the checkpointer within a context
        with checkpointer_cm as checkpointer:
            # Setup tables if needed (first time only)
            checkpointer.setup()

            # Get agent compiled with checkpointer
            agent = get_agent(checkpointer=checkpointer)

            # Prepare input with only the new message
            input_data = {
                "messages": [HumanMessage(content=request.message)],
            }

            # Run agent with checkpointing config
            config = {
                "configurable": {
                    "thread_id": conversation_id,
                },
                "recursion_limit": LANGGRAPH_RECURSION_LIMIT,
            }

            # Invoke agent (it will load previous state from checkpointer)
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

        # === PERSIST TO DATABASE ===
        try:
            # 1. Get or create conversation
            conv_uuid = persistence_service.get_or_create_conversation(
                conversation_id=conversation_id,
                user_id=request.user_id,
            )

            # 2. Save user message
            persistence_service.save_message(
                conversation_id=conv_uuid,
                role="user",
                content=request.message,
            )

            # 3. Save assistant response
            persistence_service.save_message(
                conversation_id=conv_uuid,
                role="assistant",
                content=response_text,
                metadata=metadata,
            )

            # 4. Save transaction if completed
            if result.get("transaction_id") and result.get("transaction_status") == "completed":
                persistence_service.save_transaction(
                    conversation_id=conv_uuid,
                    user_id=request.user_id,
                    external_transaction_id=result["transaction_id"],
                    recipient_phone=result.get("phone", ""),
                    amount=float(result.get("amount", 0)),
                    status="completed",
                )

                # Mark conversation as completed
                from datetime import datetime
                persistence_service.update_conversation_status(
                    conversation_id=conv_uuid,
                    status="completed",
                    ended_at=datetime.utcnow(),
                )

            logger.info("data_persisted_to_database", conversation_uuid=str(conv_uuid))

        except Exception as persist_error:
            # Log but don't fail the request if persistence fails
            logger.error(
                "persistence_error",
                error=str(persist_error),
                conversation_id=conversation_id,
                exc_info=True,
            )

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