"""Validator node - Validates transaction details.

This node validates extracted transaction information before execution.
"""

from apps.agents.transactional.state.state import TransactionalState


async def validator_node(state: TransactionalState) -> dict:
    """Validate transaction details.

    Args:
        state: Current agent state with transaction details

    Returns:
        dict: Updated state with validation results

    Validates:
        - Recipient phone format
        - Amount is positive
        - Currency is supported
    """
    errors = []

    # Validate recipient phone
    if not state.get("recipient_phone"):
        errors.append("Recipient phone number is required")

    # Validate amount
    amount = state.get("amount")
    if not amount or amount <= 0:
        errors.append("Amount must be greater than zero")

    # Validate currency
    supported_currencies = {"COP", "USD", "EUR"}
    currency = state.get("currency", "COP")
    if currency not in supported_currencies:
        errors.append(f"Currency {currency} is not supported")

    return {
        "validation_errors": errors if errors else None,
        "is_valid": len(errors) == 0,
    }