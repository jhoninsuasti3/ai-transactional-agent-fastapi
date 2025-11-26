"""Extractor node - extracts structured data from conversation."""

import structlog
from langchain_core.messages import AIMessage

from apps.agents.transactional.config import get_llm
from apps.agents.transactional.prompts.extractor import get_extraction_prompt
from apps.agents.transactional.state import TransactionalState

logger = structlog.get_logger(__name__)


def extractor_node(state: TransactionalState) -> dict:
    """Extract phone and amount from conversation messages using regex.

    Searches through all messages for phone numbers and amounts.

    Args:
        state: Current conversation state

    Returns:
        dict with extracted phone and amount
    """
    import re

    logger.info("extractor_node_start", message_count=len(state.get("messages", [])))

    phone = None
    amount = None

    # Get all message content
    messages = state.get("messages", [])
    all_text = ""

    for msg in messages:
        if hasattr(msg, "content"):
            content = msg.content
            # Handle list content
            if isinstance(content, list):
                content = " ".join(str(item) for item in content) if content else ""
            elif not isinstance(content, str):
                content = str(content)
            all_text += " " + content

    logger.info("extractor_searching", text_length=len(all_text), text_preview=all_text[:200])

    # Extract phone number (10 digits starting with 3)
    phone_pattern = r'\b(3\d{9})\b'
    phone_match = re.search(phone_pattern, all_text)
    if phone_match:
        phone = phone_match.group(1)
        logger.info("extractor_found_phone", phone=phone)

    # Extract amount (look for patterns like $75000, 75000 pesos, etc)
    amount_patterns = [
        r'\$\s*(\d{1,3}(?:[,.\s]?\d{3})*)',  # $75000 or $75,000
        r'(\d{1,3}(?:[,.\s]?\d{3})*)\s*pesos',  # 75000 pesos
        r'monto\s*:?\s*(\d{1,3}(?:[,.\s]?\d{3})*)',  # monto: 75000
        r'envía\s*\$?\s*(\d{1,3}(?:[,.\s]?\d{3})*)',  # envía $75000
        r'transferir\s*\$?\s*(\d{1,3}(?:[,.\s]?\d{3})*)',  # transferir $75000
    ]

    for pattern in amount_patterns:
        amount_match = re.search(pattern, all_text, re.IGNORECASE)
        if amount_match:
            amount_str = amount_match.group(1).replace(',', '').replace('.', '').replace(' ', '')
            try:
                amount = float(amount_str)
                logger.info("extractor_found_amount", amount=amount, pattern=pattern)
                break
            except ValueError:
                continue

    logger.info(
        "extractor_node_complete",
        phone=phone,
        amount=amount
    )

    result = {}
    if phone:
        result["phone"] = phone
    if amount:
        result["amount"] = amount

    return result
