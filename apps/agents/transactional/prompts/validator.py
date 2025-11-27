"""Validator prompt for handling validation responses.

Interprets validation API responses and generates user-friendly messages.
"""

from langchain_core.prompts import PromptTemplate

VALIDATION_RESPONSE_PROMPT = """Interpreta el resultado de validación y genera un mensaje al usuario.

DATOS ENVIADOS:
- Teléfono: {{ phone }}
- Monto: ${{ amount }} COP

RESULTADO VALIDACIÓN:
{{ validation_result }}

INSTRUCCIONES:
- Si es válido: Informa que la transacción puede proceder
- Si es inválido: Explica el error de forma clara y profesional
- Sé breve y directo

Genera el mensaje:"""

VALIDATION_RESPONSE = PromptTemplate.from_template(
    VALIDATION_RESPONSE_PROMPT, template_format="jinja2"
)


def get_validation_response(valid: bool, phone: str, amount: float, message: str) -> str:
    """Generate validation response message.

    Args:
        valid: Whether validation succeeded
        phone: Phone number
        amount: Transfer amount
        message: API response message

    Returns:
        User-friendly validation message
    """
    if valid:
        return f"✅ Validación exitosa\n\nTeléfono: {phone}\nMonto: ${amount:,.0f} COP\n\n{message}\n\n¿Confirmas esta transacción? (Responde 'sí' para confirmar)"
    return f"❌ No se puede procesar la transacción\n\nTeléfono: {phone}\nMonto: ${amount:,.0f} COP\n\nMotivo: {message}"
