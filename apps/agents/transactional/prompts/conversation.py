"""Conversation prompt for friendly money transfer assistance.

Optimized for:
- Token efficiency
- Clear, concise responses
- Guiding user through the process
"""

from langchain_core.messages import SystemMessage
from langchain_core.prompts import PromptTemplate

CONVERSATION_SYSTEM_PROMPT = """Eres un asistente bancario profesional y amigable que ayuda a enviar dinero.

OBJETIVO: Obtener número de celular (10 dígitos) y monto a enviar.

REGLAS:
1. Sé breve y claro
2. Pregunta UNA cosa a la vez
3. Si falta el teléfono, pregúntalo
4. Si falta el monto, pregúntalo
5. Una vez tengas ambos, confirma antes de proceder

ESTADO ACTUAL:
{% if phone %}✓ Teléfono: {{ phone }}{% else %}✗ Teléfono: Falta{% endif %}
{% if amount %}✓ Monto: ${{ amount }} COP{% else %}✗ Monto: Falta{% endif %}

Responde al usuario de forma natural y profesional."""

CONVERSATION_PROMPT = PromptTemplate.from_template(
    CONVERSATION_SYSTEM_PROMPT, template_format="jinja2"
)


def get_conversation_prompt(phone: str | None = None, amount: float | None = None) -> SystemMessage:
    """Generate conversation prompt with current state.

    Args:
        phone: Current phone number (if collected)
        amount: Current amount (if collected)

    Returns:
        Formatted system message
    """
    prompt_text = CONVERSATION_PROMPT.format(phone=phone, amount=amount)
    return SystemMessage(content=prompt_text)
