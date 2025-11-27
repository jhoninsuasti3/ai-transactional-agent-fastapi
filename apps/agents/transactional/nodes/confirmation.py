"""Confirmation node - handles user confirmation of transaction."""

import structlog

from apps.agents.transactional.state import TransactionalState

logger = structlog.get_logger(__name__)


def confirmation_node(state: TransactionalState) -> dict:
    """Check if user has confirmed the transaction.

    Analyzes the last user message to detect confirmation or cancellation.

    Args:
        state: Current conversation state

    Returns:
        dict with confirmed status
    """
    messages = state.get("messages", [])
    if not messages:
        logger.warning("confirmation_node_no_messages")
        return {"confirmed": False}

    # Get last user message
    last_message = None
    for msg in reversed(messages):
        if hasattr(msg, "type") and msg.type == "human":
            last_message = msg
            break

    if not last_message:
        logger.warning("confirmation_node_no_user_message")
        return {"confirmed": False}

    content = last_message.content.lower()

    # Check for confirmation keywords
    confirmation_keywords = [
        "sí",
        "si",
        "confirmo",
        "confirmar",
        "ok",
        "dale",
        "adelante",
        "seguro",
        "yes",
    ]
    cancellation_keywords = ["no", "cancelar", "cancela", "detener", "parar", "espera", "cancel"]

    is_confirmed = any(keyword in content for keyword in confirmation_keywords)
    is_cancelled = any(keyword in content for keyword in cancellation_keywords)

    logger.info(
        "confirmation_node_check",
        content=content[:50],
        is_confirmed=is_confirmed,
        is_cancelled=is_cancelled,
    )

    if is_cancelled:
        return {"confirmed": False, "needs_confirmation": False}

    return {"confirmed": is_confirmed}
