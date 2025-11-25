"""Extractor node - extracts structured data from conversation."""

import structlog
from langchain_core.messages import AIMessage

from apps.agents.transactional.config import get_llm
from apps.agents.transactional.prompts.extractor import get_extraction_prompt
from apps.agents.transactional.state import TransactionalState

logger = structlog.get_logger(__name__)


def extractor_node(state: TransactionalState) -> dict:
    """Extract phone and amount from conversation messages.

    Uses LLM with structured output to extract transaction data
    from the conversation history.

    Args:
        state: Current conversation state

    Returns:
        dict with extracted phone and amount
    """
    logger.info("extractor_node_start", message_count=len(state.get("messages", [])))

    # Get LLM
    llm = get_llm(temperature=0.0)

    # Build extraction prompt
    prompt = get_extraction_prompt()
    messages = [prompt] + state.get("messages", [])

    # Invoke LLM
    response = llm.invoke(messages)

    # Parse response - expect format "phone: XXX, amount: YYY" or structured
    content = response.content if hasattr(response, "content") else str(response)

    # Simple parsing (we'll improve this with structured output)
    phone = None
    amount = None

    lines = content.lower().split("\n")
    for line in lines:
        if "teléfono" in line or "phone" in line:
            # Extract 10 digits
            import re
            digits = re.findall(r"\d+", line)
            if digits:
                phone_candidate = "".join(digits)
                if len(phone_candidate) == 10:
                    phone = phone_candidate

        if "monto" in line or "amount" in line:
            # Extract number
            import re
            numbers = re.findall(r"[\d.]+", line)
            if numbers:
                try:
                    amount = float(numbers[0])
                except ValueError:
                    pass

    logger.info(
        "extractor_node_complete",
        phone=phone,
        amount=amount,
        extracted_from_response=content[:100] if content else None
    )

    result = {}
    if phone:
        result["phone"] = phone
    if amount:
        result["amount"] = amount

    return result
