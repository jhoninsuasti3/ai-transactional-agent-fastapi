"""Unit tests for prompt helper functions."""

import pytest
from langchain_core.messages import SystemMessage

from apps.agents.transactional.prompts.conversation import get_conversation_prompt
from apps.agents.transactional.prompts.transaction import get_transaction_result_message
from apps.agents.transactional.prompts.validator import get_validation_response
from apps.agents.transactional.prompts.extractor import get_extraction_prompt


@pytest.mark.unit
class TestConversationPrompt:
    """Test suite for conversation prompt generation."""

    def test_prompt_without_phone_and_amount(self):
        """Test prompt generation without phone and amount."""
        prompt = get_conversation_prompt()
        assert isinstance(prompt, SystemMessage)
        assert "Falta" in prompt.content
        assert "Teléfono" in prompt.content
        assert "Monto" in prompt.content

    def test_prompt_with_phone_only(self):
        """Test prompt generation with phone only."""
        prompt = get_conversation_prompt(phone="3001234567")
        assert isinstance(prompt, SystemMessage)
        assert "3001234567" in prompt.content
        assert "✓ Teléfono" in prompt.content
        assert "✗ Monto" in prompt.content

    def test_prompt_with_amount_only(self):
        """Test prompt generation with amount only."""
        prompt = get_conversation_prompt(amount=50000)
        assert isinstance(prompt, SystemMessage)
        assert "50000" in prompt.content
        assert "✗ Teléfono" in prompt.content
        assert "✓ Monto" in prompt.content

    def test_prompt_with_both_phone_and_amount(self):
        """Test prompt generation with both phone and amount."""
        prompt = get_conversation_prompt(phone="3001234567", amount=50000)
        assert isinstance(prompt, SystemMessage)
        assert "3001234567" in prompt.content
        assert "50000" in prompt.content
        assert "✓ Teléfono" in prompt.content
        assert "✓ Monto" in prompt.content


@pytest.mark.unit
class TestTransactionResultMessage:
    """Test suite for transaction result message generation."""

    def test_successful_transaction_message(self):
        """Test successful transaction message."""
        message = get_transaction_result_message(
            success=True,
            phone="3001234567",
            amount=50000,
            transaction_id="TXN-12345",
            message="Completed"
        )
        assert "✅" in message
        assert "TXN-12345" in message
        assert "3001234567" in message
        assert "50,000 COP" in message
        assert "exitosamente" in message

    def test_failed_transaction_message(self):
        """Test failed transaction message."""
        message = get_transaction_result_message(
            success=False,
            phone="3001234567",
            amount=50000,
            message="Insufficient funds"
        )
        assert "❌" in message
        assert "3001234567" in message
        assert "50,000 COP" in message
        assert "Insufficient funds" in message
        assert "no pudo completarse" in message

    def test_successful_transaction_with_large_amount(self):
        """Test successful transaction message with large amount."""
        message = get_transaction_result_message(
            success=True,
            phone="3001234567",
            amount=1000000,
            transaction_id="TXN-99999"
        )
        assert "1,000,000 COP" in message
        assert "TXN-99999" in message

    def test_successful_transaction_without_message(self):
        """Test successful transaction without additional message."""
        message = get_transaction_result_message(
            success=True,
            phone="3001234567",
            amount=50000,
            transaction_id="TXN-88888"
        )
        assert "TXN-88888" in message
        assert "exitosamente" in message


@pytest.mark.unit
class TestValidationResponse:
    """Test suite for validation response generation."""

    def test_valid_response(self):
        """Test valid validation response."""
        response = get_validation_response(
            valid=True,
            phone="3001234567",
            amount=50000,
            message="Can proceed"
        )
        assert "3001234567" in response
        assert "50,000 COP" in response
        assert "confirmar" in response or "proceder" in response

    def test_invalid_response(self):
        """Test invalid validation response."""
        response = get_validation_response(
            valid=False,
            phone="3001234567",
            amount=50000,
            message="Insufficient funds"
        )
        assert "3001234567" in response
        assert "50,000 COP" in response
        assert "Insufficient funds" in response


@pytest.mark.unit
class TestExtractionPrompt:
    """Test suite for extraction prompt generation."""

    def test_extraction_prompt_generation(self):
        """Test extraction prompt generation."""
        prompt = get_extraction_prompt()
        assert isinstance(prompt, SystemMessage)
        assert "teléfono" in prompt.content.lower() or "telefono" in prompt.content.lower()
        assert "monto" in prompt.content.lower()
