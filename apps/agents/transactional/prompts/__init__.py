"""Prompt templates for transactional agent.

All prompts use Jinja2 for dynamic interpolation and are optimized for:
- Token efficiency (concise, direct)
- Context window management (max 5-10 messages)
- Clear instructions for LLM
"""

from apps.agents.transactional.prompts.conversation import CONVERSATION_PROMPT
from apps.agents.transactional.prompts.extractor import (
    EXTRACTION_PROMPT,
    EXTRACTION_SCHEMA,
)
from apps.agents.transactional.prompts.confirmation import (
    CONFIRMATION_REQUEST,
    CONFIRMATION_DETECTION,
)
from apps.agents.transactional.prompts.validator import VALIDATION_RESPONSE
from apps.agents.transactional.prompts.transaction import TRANSACTION_RESULT

__all__ = [
    "CONVERSATION_PROMPT",
    "EXTRACTION_PROMPT",
    "EXTRACTION_SCHEMA",
    "CONFIRMATION_REQUEST",
    "CONFIRMATION_DETECTION",
    "VALIDATION_RESPONSE",
    "TRANSACTION_RESULT",
]
