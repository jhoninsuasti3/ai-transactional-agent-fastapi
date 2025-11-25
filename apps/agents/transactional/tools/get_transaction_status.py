"""Transaction status query tool.

Queries the status of a transaction using the Mock Transaction API.
"""

from typing import Annotated

from langchain_core.tools import tool
from pydantic import Field
import structlog

from apps.agents.transactional.tools.http_client import transaction_client

logger = structlog.get_logger(__name__)


@tool
def get_transaction_status_tool(
    transaction_id: Annotated[str, Field(description="Transaction ID to query")]
) -> dict:
    """Consulta el estado de una transacción previamente ejecutada.

    Llama al endpoint GET /api/v1/transactions/{transaction_id} del Mock API
    para obtener el estado actual de la transacción.

    Args:
        transaction_id: ID único de la transacción (ej: "TXN-12345")

    Returns:
        dict con:
            - transaction_id: str - ID de la transacción
            - status: str - Estado: 'pending', 'completed', 'failed'
            - recipient_phone: str - Número del destinatario
            - amount: float - Monto transferido
            - currency: str - Moneda (COP)
            - created_at: str - Timestamp de creación
            - message: str - Mensaje descriptivo
            - error: str - Error detallado (si falla la consulta)

    Examples:
        >>> get_transaction_status_tool("TXN-12345")
        {
            'transaction_id': 'TXN-12345',
            'status': 'completed',
            'recipient_phone': '3001234567',
            'amount': 50000.0,
            'currency': 'COP',
            'message': 'Transacción completada exitosamente'
        }

        >>> get_transaction_status_tool("TXN-INVALID")
        {
            'error': 'Transacción no encontrada'
        }
    """
    logger.info(
        "querying_transaction_status",
        transaction_id=transaction_id
    )

    if not transaction_id:
        return {
            "error": "Se requiere un transaction_id válido"
        }

    # Llamar al Mock API
    try:
        response = transaction_client.get(
            f"/api/v1/transactions/{transaction_id}"
        )

        logger.info(
            "transaction_status_retrieved",
            transaction_id=transaction_id,
            status=response.get("status")
        )

        return {
            "transaction_id": response.get("transaction_id"),
            "status": response.get("status"),
            "recipient_phone": response.get("recipient_phone"),
            "amount": response.get("amount"),
            "currency": response.get("currency", "COP"),
            "created_at": response.get("created_at"),
            "message": response.get("message", "Estado recuperado exitosamente"),
        }

    except Exception as e:
        logger.error(
            "status_query_failed",
            transaction_id=transaction_id,
            error=str(e)
        )

        return {
            "error": f"Error al consultar estado: {str(e)}"
        }
