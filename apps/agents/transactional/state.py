"""State management for transactional agent.

Defines the state structure that flows through the LangGraph agent.
"""

from langgraph.graph import MessagesState


class TransactionalState(MessagesState):
    """State for money transfer conversation.

    Inherits from MessagesState to get messages list with add_messages reducer.

    Attributes:
        messages: List of conversation messages (from MessagesState)
        phone: Recipient phone number (10 digits)
        amount: Amount to transfer (COP)
        validation_id: ID from validation step
        transaction_id: ID from execution step
        transaction_status: Current transaction status
        needs_confirmation: Whether user confirmation is needed
        confirmed: Whether user has confirmed the transaction
    """

    # Transaction data
    phone: str | None
    amount: float | None
    validation_id: str | None
    transaction_id: str | None
    transaction_status: str | None

    # Conversation flow control
    needs_confirmation: bool
    confirmed: bool
