"""Extractor node - Extracts intent and entities from user messages.

This node uses an LLM to extract structured information from user messages.
"""

from langchain_core.messages import AIMessage

from src.agents.transactional.state.state import TransactionalState


async def extractor_node(state: TransactionalState) -> dict:
    """Extract intent and entities from the user's message.

    Args:
        state: Current agent state with messages

    Returns:
        dict: Updated state with extracted intent and entities

    Example:
        Input: "Send $100 to 555-1234"
        Output: {
            "intent": "transaction",
            "amount": 100.0,
            "recipient_phone": "555-1234",
            "currency": "USD"
        }
    """
    # TODO: Implement LLM-based extraction with structured output
    # For now, return placeholder

    return {
        "intent": "conversation",
        "messages": [
            AIMessage(content="I'll help you with that. Let me process your request.")
        ],
    }