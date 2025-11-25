"""Phone number validation and formatting tool.

Validates Colombian phone numbers (10 digits) and formats them consistently.
"""

import re
from typing import Annotated

from langchain_core.tools import tool
from pydantic import Field


@tool
def format_phone_number_tool(
    phone: Annotated[str, Field(description="Phone number to validate and format")]
) -> dict:
    """Valida y formatea números de teléfono colombianos.

    Validaciones:
    - Debe tener exactamente 10 dígitos
    - Solo números (elimina espacios, guiones, paréntesis)
    - Debe comenzar con 3 (celulares en Colombia)

    Args:
        phone: Número de teléfono en cualquier formato

    Returns:
        dict con:
            - valid: bool - Si el número es válido
            - formatted_phone: str - Número formateado (solo si válido)
            - error: str - Mensaje de error (solo si inválido)

    Examples:
        >>> format_phone_number_tool("300-123-4567")
        {'valid': True, 'formatted_phone': '3001234567'}

        >>> format_phone_number_tool("123456")
        {'valid': False, 'error': 'El número debe tener 10 dígitos'}
    """
    # Remover todos los caracteres no numéricos
    digits_only = re.sub(r'\D', '', phone)

    # Validar longitud
    if len(digits_only) != 10:
        return {
            "valid": False,
            "error": f"El número debe tener 10 dígitos. Recibido: {len(digits_only)} dígitos"
        }

    # Validar que comience con 3 (celulares en Colombia)
    if not digits_only.startswith('3'):
        return {
            "valid": False,
            "error": "El número debe comenzar con 3 (celulares colombianos)"
        }

    return {
        "valid": True,
        "formatted_phone": digits_only
    }
