"""Extraction prompt for structured data extraction.

Extracts phone number and amount from conversation context.
Uses structured output for reliable parsing.
"""

from langchain_core.messages import SystemMessage
from langchain_core.prompts import PromptTemplate

EXTRACTION_SYSTEM_PROMPT = """Extrae el número de teléfono y monto de la conversación.

REGLAS:
- Teléfono: 10 dígitos exactos (ej: 3001234567)
- Monto: número positivo sin símbolos (ej: 50000)
- Si no encuentras alguno, devuelve null

CONVERSACIÓN:
{{ conversation_history }}

ÚLTIMO MENSAJE:
{{ last_message }}

Extrae los datos y devuélvelos en formato estructurado."""

EXTRACTION_PROMPT = PromptTemplate.from_template(EXTRACTION_SYSTEM_PROMPT, template_format="jinja2")

# Schema para structured output
EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "phone": {
            "type": ["string", "null"],
            "description": "Número de celular de 10 dígitos",
            "pattern": "^[0-9]{10}$",
        },
        "amount": {
            "type": ["number", "null"],
            "description": "Monto a enviar (solo número, sin símbolos)",
            "minimum": 0,
        },
    },
    "required": ["phone", "amount"],
}


def get_extraction_prompt():
    """Generate extraction prompt.

    Returns:
        System message for extraction
    """
    return SystemMessage(content=EXTRACTION_SYSTEM_PROMPT)
