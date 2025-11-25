"""Transaction validation tool.

Validates if a transaction can be processed using the Mock Transaction API.
"""

from typing import Annotated

from langchain_core.tools import tool
from pydantic import Field
import structlog

from apps.agents.transactional.tools.http_client import transaction_client

logger = structlog.get_logger(__name__)


@tool
def validate_transaction_tool(
    phone: Annotated[str, Field(description="Recipient phone number (10 digits)")],
    amount: Annotated[float, Field(description="Amount to transfer (must be > 0)", gt=0)]
) -> dict:
    """Valida si una transacción de dinero puede ser procesada.

    Llama al endpoint POST /api/v1/transactions/validate del Mock API
    para verificar si la transacción es posible.

    Args:
        phone: Número de celular del destinatario (10 dígitos)
        amount: Monto a enviar (debe ser mayor a 0)

    Returns:
        dict con:
            - valid: bool - Si la transacción puede procesarse
            - message: str - Mensaje descriptivo
            - validation_id: str - ID de validación (si exitosa)
            - error: str - Error detallado (si falla)

    Examples:
        >>> validate_transaction_tool("3001234567", 50000)
        {
            'valid': True,
            'message': 'Transacción válida',
            'validation_id': 'VAL-12345'
        }

        >>> validate_transaction_tool("3001234567", -100)
        {
            'valid': False,
            'error': 'El monto debe ser mayor a 0'
        }
    """
    logger.info(
        "validating_transaction",
        phone=phone,
        amount=amount
    )

    # Validaciones locales
    if amount <= 0:
        return {
            "valid": False,
            "error": "El monto debe ser mayor a 0"
        }

    if len(phone) != 10:
        return {
            "valid": False,
            "error": "El número debe tener 10 dígitos"
        }

    # Llamar al Mock API
    try:
        response = transaction_client.post(
            "/api/v1/transactions/validate",
            json={
                "recipient_phone": phone,
                "amount": amount,
                "currency": "COP"
            }
        )

        # Mock API returns "is_valid", normalize to "valid"
        is_valid = response.get("is_valid", response.get("valid", False))

        logger.info(
            "validation_response",
            valid=is_valid,
            validation_id=response.get("validation_id")
        )

        return {
            "valid": is_valid,
            "message": response.get("message", "Validación completada"),
            "validation_id": response.get("validation_id"),
        }

    except Exception as e:
        logger.error(
            "validation_failed",
            phone=phone,
            amount=amount,
            error=str(e)
        )

        return {
            "valid": False,
            "error": f"Error al validar transacción: {str(e)}"
        }
