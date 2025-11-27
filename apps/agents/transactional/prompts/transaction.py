"""Transaction prompt for success/failure messages.

Generates appropriate messages based on transaction results.
"""

from langchain_core.prompts import PromptTemplate

TRANSACTION_RESULT_PROMPT = """Genera el mensaje final de la transacción.

RESULTADO:
{{ transaction_result }}

INSTRUCCIONES:
- Si exitosa: Confirma y da el ID de transacción
- Si falló: Explica el error y sugiere qué hacer
- Sé empático y profesional
- Máximo 2 oraciones

Mensaje:"""

TRANSACTION_RESULT = PromptTemplate.from_template(
    TRANSACTION_RESULT_PROMPT, template_format="jinja2"
)


def get_transaction_result_message(
    success: bool, phone: str, amount: float, transaction_id: str | None = None, message: str = ""
) -> str:
    """Generate transaction result message.

    Args:
        success: Whether transaction succeeded
        phone: Phone number
        amount: Transfer amount
        transaction_id: Transaction ID (if successful)
        message: API response message

    Returns:
        User-friendly transaction result message
    """
    if success:
        return f"✅ Transacción completada exitosamente\n\nID: {transaction_id}\nDestino: {phone}\nMonto: ${amount:,.0f} COP\n\n{message}"
    return f"❌ La transacción no pudo completarse\n\nDestino: {phone}\nMonto: ${amount:,.0f} COP\n\nMotivo: {message}\n\nPor favor, intenta nuevamente o contacta soporte."
