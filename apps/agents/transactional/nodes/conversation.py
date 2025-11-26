"""Conversation node - handles natural language interaction with user."""

import structlog

from apps.agents.transactional.config import get_llm
from apps.agents.transactional.prompts.conversation import get_conversation_prompt
from apps.agents.transactional.state import TransactionalState

logger = structlog.get_logger(__name__)


def conversation_node(state: TransactionalState) -> dict:
    """Generate conversational response guiding user through transaction flow.

    The conversation is purely conversational - all data extraction and validation
    is handled by dedicated nodes using deterministic logic (regex).

    Args:
        state: Current conversation state

    Returns:
        dict with updated messages
    """
    logger.info(
        "conversation_node_start",
        phone=state.get("phone"),
        amount=state.get("amount"),
        needs_confirmation=state.get("needs_confirmation"),
        confirmed=state.get("confirmed"),
        message_count=len(state.get("messages", []))
    )

    # Get LLM without tools (purely conversational)
    llm = get_llm()

    # Build prompt with current state
    prompt = get_conversation_prompt(
        phone=state.get("phone"),
        amount=state.get("amount")
    )

    # Invoke LLM
    messages = [prompt] + state.get("messages", [])
    response = llm.invoke(messages)

    logger.info(
        "conversation_node_complete",
        response_length=len(response.content) if response.content else 0
    )

    return {"messages": [response]}
