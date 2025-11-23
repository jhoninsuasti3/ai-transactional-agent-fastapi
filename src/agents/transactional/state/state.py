"""State definition for the transactional agent.

This module defines the state structure that flows through the agent graph.
"""

from typing import Literal

from langgraph.graph import MessagesState


class TransactionalState(MessagesState):
    """State for the transactional agent.

    Extends MessagesState to include transaction-specific fields.

    Attributes:
        messages: List of chat messages (from MessagesState)
        intent: Extracted user intent (conversation, transaction, etc.)
        recipient_phone: Extracted recipient phone number
        amount: Extracted transaction amount
        currency: Currency code (default: COP)
        validation_errors: List of validation errors if any
        transaction_id: External service transaction ID
        transaction_status: Status of the transaction
        conversation_id: Database conversation ID
        user_id: User identifier
    """

    # Intent classification
    intent: str | None = None

    # Transaction details
    recipient_phone: str | None = None
    amount: float | None = None
    currency: str = "COP"

    # Validation
    validation_errors: list[str] | None = None
    is_valid: bool = False

    # Transaction execution
    transaction_id: str | None = None
    transaction_status: Literal["pending", "completed", "failed"] | None = None

    # Context
    conversation_id: int | None = None
    user_id: str | None = None