"""Conversation node - Handles general conversation.

This node manages conversational responses when no transaction is detected.
"""

from langchain_core.messages import AIMessage

from apps.agents.transactional.state.state import TransactionalState


async def conversation_node(state: TransactionalState) -> dict:
    """Handle general conversation.

    Args:
        state: Current agent state

    Returns:
        dict: Updated state with conversational response

    Example:
        Input: "Hello, how are you?"
        Output: Friendly greeting response
    """
    # TODO: Implement conversational LLM
    # For now, return placeholder

    return {
        "messages": [
            AIMessage(
                content="Hello! I'm your transactional assistant. How can I help you today?"
            )
        ]
    }