"""Intent routing - Routes based on extracted user intent.

This module determines the next node based on the extracted intent.
"""

from typing import Literal

from apps.agents.transactional.state import TransactionalState


def intent_route(state: TransactionalState) -> Literal["conversation", "transaction"]:
    """Route based on extracted intent.

    Args:
        state: Current agent state with extracted intent

    Returns:
        str: Next node to execute ("conversation" or "transaction")

    Examples:
        >>> state = {"intent": "transaction"}
        >>> intent_route(state)
        'transaction'

        >>> state = {"intent": "conversation"}
        >>> intent_route(state)
        'conversation'
    """
    intent = state.get("intent", "conversation")

    if intent == "transaction":
        return "transaction"

    # Default to conversation for all other intents
    return "conversation"
