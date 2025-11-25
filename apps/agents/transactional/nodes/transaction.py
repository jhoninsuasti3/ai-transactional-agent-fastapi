"""Transaction node - executes the money transfer."""

import structlog
from langchain_core.messages import AIMessage

from apps.agents.transactional.prompts.transaction import get_transaction_result_message
from apps.agents.transactional.state import TransactionalState
from apps.agents.transactional.tools import execute_transaction_tool

logger = structlog.get_logger(__name__)


def transaction_node(state: TransactionalState) -> dict:
    """Execute the transaction using Mock API.

    Calls execute_transaction_tool and generates result message.

    Args:
        state: Current conversation state with phone, amount, validation_id

    Returns:
        dict with transaction_id, transaction_status, and message
    """
    phone = state.get("phone")
    amount = state.get("amount")
    validation_id = state.get("validation_id")

    logger.info(
        "transaction_node_start",
        phone=phone,
        amount=amount,
        validation_id=validation_id
    )

    if not phone or not amount:
        logger.error("transaction_node_missing_data", phone=phone, amount=amount)
        return {
            "transaction_status": "failed",
            "messages": [
                AIMessage(content="Error: No se puede ejecutar sin teléfono y monto.")
            ],
        }

    # Execute transaction
    result = execute_transaction_tool.invoke({
        "phone": phone,
        "amount": amount,
        "validation_id": validation_id
    })

    if result.get("success"):
        # Success
        message = get_transaction_result_message(
            success=True,
            phone=phone,
            amount=amount,
            transaction_id=result.get("transaction_id"),
            message=result.get("message", "")
        )

        logger.info(
            "transaction_node_success",
            transaction_id=result.get("transaction_id"),
            status=result.get("status")
        )

        return {
            "transaction_id": result.get("transaction_id"),
            "transaction_status": result.get("status", "completed"),
            "messages": [AIMessage(content=message)],
        }
    else:
        # Failed
        error = result.get("error", "Error desconocido")
        message = get_transaction_result_message(
            success=False,
            phone=phone,
            amount=amount,
            message=error
        )

        logger.error(
            "transaction_node_failed",
            error=error,
            status=result.get("status")
        )

        return {
            "transaction_status": "failed",
            "messages": [AIMessage(content=message)],
        }
