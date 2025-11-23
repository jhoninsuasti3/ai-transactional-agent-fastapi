"""Validation routing - Routes based on validation results.

This module determines the next node based on transaction validation.
"""

from typing import Literal

from apps.agents.transactional.state.state import TransactionalState


def validation_route(state: TransactionalState) -> Literal["valid", "invalid"]:
    """Route based on validation results.

    Args:
        state: Current agent state with validation results

    Returns:
        str: Next node to execute ("valid" or "invalid")

    Examples:
        >>> state = {"is_valid": True}
        >>> validation_route(state)
        'valid'

        >>> state = {"is_valid": False}
        >>> validation_route(state)
        'invalid'
    """
    is_valid = state.get("is_valid", False)

    if is_valid:
        return "valid"

    return "invalid"