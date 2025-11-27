"""Multi-LLM configuration for transactional agent.

Supports both OpenAI and Anthropic models with environment-based selection.
Uses LangChain's init_chat_model for unified interface.
"""

from enum import Enum
from typing import Any

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from apps.orchestrator.settings import settings


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class LLMModel(str, Enum):
    """Available models per provider."""

    # OpenAI models
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4O = "gpt-4o"
    GPT_4_TURBO = "gpt-4-turbo"

    # Anthropic models
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet-20241022"
    CLAUDE_3_5_HAIKU = "claude-3-5-haiku-20241022"
    CLAUDE_3_OPUS = "claude-3-opus-20240229"


def get_llm(
    provider: str | None = None,
    model: str | None = None,
    temperature: float = 0.0,
    **kwargs: Any,
) -> BaseChatModel:
    """Get configured LLM instance based on provider.

    Args:
        provider: LLM provider ("openai" or "anthropic"). Defaults to settings.LLM_PROVIDER.
        model: Specific model to use. Defaults to settings.LLM_MODEL.
        temperature: Model temperature (0.0 = deterministic, 1.0 = creative).
        **kwargs: Additional arguments passed to init_chat_model.

    Returns:
        BaseChatModel: Configured chat model instance.

    Example:
        >>> llm = get_llm(provider="openai", model="gpt-4o-mini")
        >>> llm = get_llm(provider="anthropic", model="claude-3-5-sonnet")
        >>> llm = get_llm()  # Uses environment config
    """
    provider = (
        provider or settings.LLM_MODEL.split(":")[0] if ":" in settings.LLM_MODEL else "openai"
    )
    model = (
        model or settings.LLM_MODEL.split(":")[-1]
        if ":" in settings.LLM_MODEL
        else settings.LLM_MODEL
    )

    # Build model string for init_chat_model
    model_string = f"{provider}:{model}"

    # Prepare kwargs
    init_kwargs = {
        "temperature": temperature,
        **kwargs,
    }

    # Add API keys if not already in environment
    if provider == LLMProvider.OPENAI and not init_kwargs.get("api_key"):
        init_kwargs["api_key"] = settings.OPENAI_API_KEY
    elif provider == LLMProvider.ANTHROPIC and not init_kwargs.get("api_key"):
        init_kwargs["api_key"] = settings.ANTHROPIC_API_KEY

    # Initialize model using LangChain's unified interface
    return init_chat_model(model_string, **init_kwargs)


def get_structured_llm(
    output_schema: type,
    provider: str | None = None,
    model: str | None = None,
    **kwargs: Any,
) -> BaseChatModel:
    """Get LLM configured for structured output.

    Args:
        output_schema: Pydantic model for structured output.
        provider: LLM provider.
        model: Specific model.
        **kwargs: Additional arguments.

    Returns:
        BaseChatModel: LLM with structured output binding.

    Example:
        >>> from pydantic import BaseModel
        >>> class TransactionData(BaseModel):
        ...     phone: str
        ...     amount: float
        >>> llm = get_structured_llm(TransactionData)
        >>> result = llm.invoke("Send 50000 to 3001234567")
        >>> result.phone  # "3001234567"
    """
    llm = get_llm(provider=provider, model=model, **kwargs)

    # Bind structured output schema
    return llm.with_structured_output(output_schema)


# Presets for common configurations
def get_conversation_llm() -> BaseChatModel:
    """Get LLM optimized for conversation (higher temperature)."""
    return get_llm(temperature=settings.LLM_TEMPERATURE)


def get_extraction_llm() -> BaseChatModel:
    """Get LLM optimized for data extraction (low temperature)."""
    return get_llm(temperature=0.0)


def get_validation_llm() -> BaseChatModel:
    """Get LLM optimized for validation (deterministic)."""
    return get_llm(temperature=0.0)
