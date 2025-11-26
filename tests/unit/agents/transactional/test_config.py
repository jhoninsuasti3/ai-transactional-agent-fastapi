"""Unit tests for LLM configuration."""

import pytest
from unittest.mock import patch, MagicMock
from pydantic import BaseModel

from apps.agents.transactional.config import (
    LLMProvider,
    LLMModel,
    get_llm,
    get_structured_llm,
    get_conversation_llm,
    get_extraction_llm,
    get_validation_llm,
)


@pytest.mark.unit
class TestLLMEnums:
    """Test LLM enums."""

    def test_llm_provider_values(self):
        """Test LLM provider enum values."""
        assert LLMProvider.OPENAI == "openai"
        assert LLMProvider.ANTHROPIC == "anthropic"

    def test_llm_model_openai_values(self):
        """Test OpenAI model enum values."""
        assert LLMModel.GPT_4O_MINI == "gpt-4o-mini"
        assert LLMModel.GPT_4O == "gpt-4o"
        assert LLMModel.GPT_4_TURBO == "gpt-4-turbo"

    def test_llm_model_anthropic_values(self):
        """Test Anthropic model enum values."""
        assert LLMModel.CLAUDE_3_5_SONNET == "claude-3-5-sonnet-20241022"
        assert LLMModel.CLAUDE_3_5_HAIKU == "claude-3-5-haiku-20241022"
        assert LLMModel.CLAUDE_3_OPUS == "claude-3-opus-20240229"


@pytest.mark.unit
class TestGetLLM:
    """Test get_llm function."""

    @patch('apps.agents.transactional.config.init_chat_model')
    def test_get_llm_with_openai_provider(self, mock_init):
        """Test getting LLM with OpenAI provider."""
        mock_llm = MagicMock()
        mock_init.return_value = mock_llm

        result = get_llm(provider="openai", model="gpt-4o-mini", temperature=0.5, api_key="test-key")

        assert result == mock_llm
        mock_init.assert_called_once()
        call_args = mock_init.call_args
        assert call_args[0][0] == "openai:gpt-4o-mini"
        assert call_args[1]["temperature"] == 0.5
        assert call_args[1]["api_key"] == "test-key"

    @patch('apps.agents.transactional.config.init_chat_model')
    def test_get_llm_with_anthropic_provider(self, mock_init):
        """Test getting LLM with Anthropic provider."""
        mock_llm = MagicMock()
        mock_init.return_value = mock_llm

        result = get_llm(provider="anthropic", model="claude-3-5-sonnet-20241022", temperature=0.7, api_key="test-key")

        assert result == mock_llm
        mock_init.assert_called_once()
        call_args = mock_init.call_args
        assert call_args[0][0] == "anthropic:claude-3-5-sonnet-20241022"
        assert call_args[1]["temperature"] == 0.7
        assert call_args[1]["api_key"] == "test-key"

    @patch('apps.agents.transactional.config.init_chat_model')
    @patch('apps.agents.transactional.config.settings')
    def test_get_llm_defaults_from_settings(self, mock_settings, mock_init):
        """Test getting LLM uses settings defaults."""
        mock_settings.LLM_MODEL = "openai:gpt-4o-mini"
        mock_settings.OPENAI_API_KEY = "default-key"
        mock_llm = MagicMock()
        mock_init.return_value = mock_llm

        result = get_llm()

        assert result == mock_llm
        mock_init.assert_called_once()

    @patch('apps.agents.transactional.config.init_chat_model')
    def test_get_llm_with_custom_kwargs(self, mock_init):
        """Test getting LLM with additional kwargs."""
        mock_llm = MagicMock()
        mock_init.return_value = mock_llm

        result = get_llm(
            provider="openai",
            model="gpt-4o",
            temperature=0.8,
            max_tokens=1000,
            custom_param="value",
            api_key="test-key"
        )

        assert result == mock_llm
        call_args = mock_init.call_args[1]
        assert call_args["max_tokens"] == 1000
        assert call_args["custom_param"] == "value"

    @patch('apps.agents.transactional.config.init_chat_model')
    @patch('apps.agents.transactional.config.settings')
    def test_get_llm_without_colon_in_model(self, mock_settings, mock_init):
        """Test getting LLM when LLM_MODEL doesn't contain colon."""
        mock_settings.LLM_MODEL = "gpt-4o-mini"
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_llm = MagicMock()
        mock_init.return_value = mock_llm

        result = get_llm()

        assert result == mock_llm
        # Should default to openai when no colon
        call_args = mock_init.call_args
        assert "openai:" in call_args[0][0]

    @patch('apps.agents.transactional.config.init_chat_model')
    def test_get_llm_with_api_key_in_kwargs(self, mock_init):
        """Test that provided api_key in kwargs is not overridden."""
        mock_llm = MagicMock()
        mock_init.return_value = mock_llm

        result = get_llm(provider="openai", model="gpt-4o", api_key="custom-key")

        assert result == mock_llm
        call_args = mock_init.call_args[1]
        assert call_args["api_key"] == "custom-key"


@pytest.mark.unit
class TestGetStructuredLLM:
    """Test get_structured_llm function."""

    @patch('apps.agents.transactional.config.get_llm')
    def test_get_structured_llm(self, mock_get_llm):
        """Test getting structured LLM."""
        class TestSchema(BaseModel):
            field: str

        mock_llm = MagicMock()
        mock_structured = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured
        mock_get_llm.return_value = mock_llm

        result = get_structured_llm(TestSchema, provider="openai", model="gpt-4o")

        assert result == mock_structured
        mock_get_llm.assert_called_once_with(provider="openai", model="gpt-4o")
        mock_llm.with_structured_output.assert_called_once_with(TestSchema)

    @patch('apps.agents.transactional.config.get_llm')
    def test_get_structured_llm_with_kwargs(self, mock_get_llm):
        """Test getting structured LLM with additional kwargs."""
        class TestSchema(BaseModel):
            name: str
            value: int

        mock_llm = MagicMock()
        mock_structured = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured
        mock_get_llm.return_value = mock_llm

        result = get_structured_llm(
            TestSchema,
            provider="anthropic",
            model="claude-3-5-haiku-20241022",
            temperature=0.0
        )

        assert result == mock_structured
        mock_get_llm.assert_called_once_with(
            provider="anthropic",
            model="claude-3-5-haiku-20241022",
            temperature=0.0
        )


@pytest.mark.unit
class TestPresetFunctions:
    """Test preset LLM configuration functions."""

    @patch('apps.agents.transactional.config.get_llm')
    @patch('apps.agents.transactional.config.settings')
    def test_get_conversation_llm(self, mock_settings, mock_get_llm):
        """Test getting conversation LLM with configured temperature."""
        mock_settings.LLM_TEMPERATURE = 0.7
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm

        result = get_conversation_llm()

        assert result == mock_llm
        mock_get_llm.assert_called_once_with(temperature=0.7)

    @patch('apps.agents.transactional.config.get_llm')
    def test_get_extraction_llm(self, mock_get_llm):
        """Test getting extraction LLM with low temperature."""
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm

        result = get_extraction_llm()

        assert result == mock_llm
        mock_get_llm.assert_called_once_with(temperature=0.0)

    @patch('apps.agents.transactional.config.get_llm')
    def test_get_validation_llm(self, mock_get_llm):
        """Test getting validation LLM with deterministic temperature."""
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm

        result = get_validation_llm()

        assert result == mock_llm
        mock_get_llm.assert_called_once_with(temperature=0.0)
