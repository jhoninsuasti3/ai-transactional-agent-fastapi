"""Transaction node - Executes validated transactions.

This node executes transactions via the external service.
"""

from langchain_core.messages import AIMessage

from apps.agents.transactional.state.state import TransactionalState


async def transaction_node(state: TransactionalState) -> dict:
    """Execute the transaction.

    Args:
        state: Current agent state with validated transaction details

    Returns:
        dict: Updated state with transaction results

    Calls:
        External transaction service to execute the transfer
    """
    # TODO: Implement transaction execution via external service
    # For now, return placeholder

    recipient = state.get("recipient_phone", "unknown")
    amount = state.get("amount", 0)
    currency = state.get("currency", "COP")

    return {
        "transaction_status": "completed",
        "transaction_id": "TXN-12345",
        "messages": [
            AIMessage(
                content=f"Transaction completed successfully! "
                f"Sent {amount} {currency} to {recipient}. "
                f"Transaction ID: TXN-12345"
            )
        ],
    }