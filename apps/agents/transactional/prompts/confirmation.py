"""Confirmation prompt for transaction approval.

Generates clear confirmation message and detects user's response.
"""

from langchain_core.prompts import PromptTemplate

CONFIRMATION_REQUEST_PROMPT = """Genera un mensaje de confirmación claro y profesional.

DATOS:
- Teléfono: {{ phone }}
- Monto: ${{ amount }} COP

Pregunta al usuario si confirma el envío. Sé breve."""

CONFIRMATION_REQUEST = PromptTemplate.from_template(
    CONFIRMATION_REQUEST_PROMPT,
    template_format="jinja2"
)


CONFIRMATION_DETECTION_PROMPT = """Determina si el usuario confirmó o canceló la transacción.

MENSAJE DEL USUARIO: {{ user_message }}

REGLAS:
- "sí", "confirmo", "adelante", "ok" → confirmed
- "no", "cancela", "espera" → cancelled
- Cualquier duda → pending

Responde solo: confirmed, cancelled o pending"""

CONFIRMATION_DETECTION = PromptTemplate.from_template(
    CONFIRMATION_DETECTION_PROMPT,
    template_format="jinja2"
)
