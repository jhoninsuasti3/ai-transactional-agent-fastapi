"""Transaction execution tool.

Executes confirmed money transfers using the Mock Transaction API.
"""

from typing import Annotated

from langchain_core.tools import tool
from pydantic import Field
import structlog

from apps.agents.transactional.tools.http_client import transaction_client

logger = structlog.get_logger(__name__)


@tool
def execute_transaction_tool(
    phone: Annotated[str, Field(description="Recipient phone number (10 digits)")],
    amount: Annotated[float, Field(description="Amount to transfer (must be > 0)", gt=0)],
    validation_id: Annotated[str | None, Field(description="Validation ID from previous validation")] = None
) -> dict:
    """Ejecuta una transacción de envío de dinero previamente confirmada.

    Llama al endpoint POST /api/v1/transactions/execute del Mock API
    para procesar la transferencia.

    IMPORTANTE: Solo debe ejecutarse después de que el usuario haya confirmado explícitamente.

    Args:
        phone: Número de celular del destinatario (10 dígitos)
        amount: Monto a enviar (debe ser mayor a 0)
        validation_id: ID de validación previo (opcional)

    Returns:
        dict con:
            - success: bool - Si la transacción fue exitosa
            - transaction_id: str - ID único de la transacción (si exitosa)
            - status: str - Estado: 'completed', 'pending', 'failed'
            - message: str - Mensaje descriptivo
            - error: str - Error detallado (si falla)

    Examples:
        >>> execute_transaction_tool("3001234567", 50000, "VAL-12345")
        {
            'success': True,
            'transaction_id': 'TXN-67890',
            'status': 'completed',
            'message': 'Transacción exitosa'
        }

        >>> execute_transaction_tool("3001234567", 999999999)
        {
            'success': False,
            'status': 'failed',
            'error': 'Monto excede el límite permitido'
        }
    """
    logger.info(
        "executing_transaction",
        phone=phone,
        amount=amount,
        validation_id=validation_id
    )

    # Validaciones locales
    if amount <= 0:
        return {
            "success": False,
            "status": "failed",
            "error": "El monto debe ser mayor a 0"
        }

    if len(phone) != 10:
        return {
            "success": False,
            "status": "failed",
            "error": "El número debe tener 10 dígitos"
        }

    # Llamar al Mock API
    try:
        payload = {
            "recipient_phone": phone,
            "amount": amount,
            "currency": "COP"
        }

        if validation_id:
            payload["validation_id"] = validation_id

        response = transaction_client.post(
            "/api/v1/transactions/execute",
            json=payload
        )

        # Determine success from status (Mock API doesn't return "success" field)
        status = response.get("status", "unknown")
        is_successful = status in ("completed", "pending")

        logger.info(
            "transaction_executed",
            success=is_successful,
            transaction_id=response.get("transaction_id"),
            status=status
        )

        return {
            "success": is_successful,
            "transaction_id": response.get("transaction_id"),
            "status": status,
            "message": response.get("message", "Transacción procesada"),
        }

    except Exception as e:
        logger.error(
            "transaction_execution_failed",
            phone=phone,
            amount=amount,
            error=str(e)
        )

        return {
            "success": False,
            "status": "failed",
            "error": f"Error al ejecutar transacción: {str(e)}"
        }
