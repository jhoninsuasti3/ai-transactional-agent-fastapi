"""Validator node - validates transaction with Mock API."""

import structlog
from langchain_core.messages import AIMessage

from apps.agents.transactional.prompts.validator import get_validation_response
from apps.agents.transactional.state import TransactionalState
from apps.agents.transactional.tools import validate_transaction_tool

logger = structlog.get_logger(__name__)


def validator_node(state: TransactionalState) -> dict:
    """Validate transaction using Mock API.

    Calls validate_transaction_tool and updates state with result.

    Args:
        state: Current conversation state with phone and amount

    Returns:
        dict with validation_id, needs_confirmation, and message
    """
    phone = state.get("phone")
    amount = state.get("amount")

    logger.info("validator_node_start", phone=phone, amount=amount)

    if not phone or not amount:
        logger.warning("validator_node_missing_data", phone=phone, amount=amount)
        return {
            "messages": [
                AIMessage(content="Error: Faltan datos (teléfono o monto) para validar.")
            ],
            "needs_confirmation": False,
        }

    # Call validation tool
    result = validate_transaction_tool.invoke({"phone": phone, "amount": amount})

    if result.get("valid"):
        # Success - prepare for confirmation
        message = get_validation_response(
            valid=True, phone=phone, amount=amount, message=result.get("message", "")
        )

        logger.info(
            "validator_node_success",
            validation_id=result.get("validation_id"),
            phone=phone,
            amount=amount,
        )

        return {
            "validation_id": result.get("validation_id"),
            "needs_confirmation": True,
            "messages": [AIMessage(content=message)],
        }
    else:
        # Validation failed
        error = result.get("error", "Error desconocido")
        message = get_validation_response(
            valid=False, phone=phone, amount=amount, message=error
        )

        logger.warning("validator_node_failed", error=error, phone=phone, amount=amount)

        return {
            "needs_confirmation": False,
            "messages": [AIMessage(content=message)],
        }
