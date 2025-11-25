"""Conversation node - handles natural language interaction with user."""

import structlog
from langchain_core.messages import AIMessage

from apps.agents.transactional.config import get_llm
from apps.agents.transactional.prompts.conversation import get_conversation_prompt
from apps.agents.transactional.state import TransactionalState
from apps.agents.transactional.tools import format_phone_number_tool

logger = structlog.get_logger(__name__)


def conversation_node(state: TransactionalState) -> dict:
    """Generate conversational response to collect phone and amount.

    Uses LLM with format_phone_number_tool to interact naturally with user
    and collect/validate transaction details.

    Args:
        state: Current conversation state

    Returns:
        dict with updated messages
    """
    logger.info(
        "conversation_node_start",
        phone=state.get("phone"),
        amount=state.get("amount"),
        message_count=len(state.get("messages", []))
    )

    # Get LLM with tools
    llm = get_llm()
    llm_with_tools = llm.bind_tools([format_phone_number_tool])

    # Build prompt with current state
    prompt = get_conversation_prompt(
        phone=state.get("phone"),
        amount=state.get("amount")
    )

    # Invoke LLM
    messages = [prompt] + state.get("messages", [])
    response = llm_with_tools.invoke(messages)

    logger.info(
        "conversation_node_complete",
        has_tool_calls=bool(response.tool_calls),
        response_length=len(response.content) if response.content else 0
    )

    return {"messages": [response]}
