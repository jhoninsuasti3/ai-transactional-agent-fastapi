"""Unit tests for extractor node."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage

from apps.agents.transactional.nodes.extractor import extractor_node


@pytest.mark.unit
class TestExtractorNode:
    """Test suite for extractor node."""

    @patch('apps.agents.transactional.nodes.extractor.get_llm')
    @patch('apps.agents.transactional.nodes.extractor.get_extraction_prompt')
    def test_extractor_extracts_phone_and_amount(self, mock_prompt, mock_get_llm):
        """Test extractor successfully extracts phone and amount."""
        # Setup mock LLM response
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Teléfono: 3001234567\nMonto: 50000"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        mock_prompt.return_value = Mock()

        # Create state
        state = {
            "messages": [
                HumanMessage(content="Quiero enviar 50000 al 3001234567")
            ]
        }

        # Execute
        result = extractor_node(state)

        # Assert
        assert result["phone"] == "3001234567"
        assert result["amount"] == 50000
        mock_get_llm.assert_called_once_with(temperature=0.0)
        mock_llm.invoke.assert_called_once()

    @patch('apps.agents.transactional.nodes.extractor.get_llm')
    @patch('apps.agents.transactional.nodes.extractor.get_extraction_prompt')
    def test_extractor_extracts_phone_only(self, mock_prompt, mock_get_llm):
        """Test extractor extracts only phone when amount not present."""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Teléfono: 3009876543\nMonto: no detectado"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        mock_prompt.return_value = Mock()

        state = {
            "messages": [HumanMessage(content="Al 3009876543")]
        }

        result = extractor_node(state)

        assert result["phone"] == "3009876543"
        assert "amount" not in result

    @patch('apps.agents.transactional.nodes.extractor.get_llm')
    @patch('apps.agents.transactional.nodes.extractor.get_extraction_prompt')
    def test_extractor_extracts_amount_only(self, mock_prompt, mock_get_llm):
        """Test extractor extracts only amount when phone not present."""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Teléfono: no detectado\nMonto: 75000"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        mock_prompt.return_value = Mock()

        state = {
            "messages": [HumanMessage(content="75000 pesos")]
        }

        result = extractor_node(state)

        assert "phone" not in result
        assert result["amount"] == 75000

    @patch('apps.agents.transactional.nodes.extractor.get_llm')
    @patch('apps.agents.transactional.nodes.extractor.get_extraction_prompt')
    def test_extractor_returns_empty_when_nothing_found(self, mock_prompt, mock_get_llm):
        """Test extractor returns empty dict when nothing extracted."""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "No se detectó información de transacción"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        mock_prompt.return_value = Mock()

        state = {
            "messages": [HumanMessage(content="Hola")]
        }

        result = extractor_node(state)

        assert result == {}

    @patch('apps.agents.transactional.nodes.extractor.get_llm')
    @patch('apps.agents.transactional.nodes.extractor.get_extraction_prompt')
    def test_extractor_handles_phone_in_english(self, mock_prompt, mock_get_llm):
        """Test extractor handles 'phone' keyword in English."""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Phone: 3001112233\nAmount: 10000"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        mock_prompt.return_value = Mock()

        state = {
            "messages": [HumanMessage(content="Send 10000 to 3001112233")]
        }

        result = extractor_node(state)

        assert result["phone"] == "3001112233"
        assert result["amount"] == 10000

    @patch('apps.agents.transactional.nodes.extractor.get_llm')
    @patch('apps.agents.transactional.nodes.extractor.get_extraction_prompt')
    def test_extractor_ignores_invalid_phone_length(self, mock_prompt, mock_get_llm):
        """Test extractor ignores phone numbers that aren't 10 digits."""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Teléfono: 300123\nMonto: 50000"  # Only 6 digits
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        mock_prompt.return_value = Mock()

        state = {
            "messages": [HumanMessage(content="Test")]
        }

        result = extractor_node(state)

        assert "phone" not in result
        assert result["amount"] == 50000

    @patch('apps.agents.transactional.nodes.extractor.get_llm')
    @patch('apps.agents.transactional.nodes.extractor.get_extraction_prompt')
    def test_extractor_handles_invalid_amount(self, mock_prompt, mock_get_llm):
        """Test extractor handles invalid amount format gracefully."""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Teléfono: 3001234567\nMonto: invalid"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        mock_prompt.return_value = Mock()

        state = {
            "messages": [HumanMessage(content="Test")]
        }

        result = extractor_node(state)

        assert result["phone"] == "3001234567"
        assert "amount" not in result

    @patch('apps.agents.transactional.nodes.extractor.get_llm')
    @patch('apps.agents.transactional.nodes.extractor.get_extraction_prompt')
    def test_extractor_handles_decimal_amount(self, mock_prompt, mock_get_llm):
        """Test extractor handles decimal amounts."""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Teléfono: 3001234567\nMonto: 50000.50"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        mock_prompt.return_value = Mock()

        state = {
            "messages": [HumanMessage(content="Test")]
        }

        result = extractor_node(state)

        assert result["phone"] == "3001234567"
        assert result["amount"] == 50000.50

    @patch('apps.agents.transactional.nodes.extractor.get_llm')
    @patch('apps.agents.transactional.nodes.extractor.get_extraction_prompt')
    def test_extractor_handles_response_without_content_attribute(self, mock_prompt, mock_get_llm):
        """Test extractor handles response that doesn't have content attribute."""
        mock_llm = Mock()
        mock_response = "Teléfono: 3001234567\nMonto: 25000"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        mock_prompt.return_value = Mock()

        state = {
            "messages": [HumanMessage(content="Test")]
        }

        result = extractor_node(state)

        assert result["phone"] == "3001234567"
        assert result["amount"] == 25000

    @patch('apps.agents.transactional.nodes.extractor.get_llm')
    @patch('apps.agents.transactional.nodes.extractor.get_extraction_prompt')
    def test_extractor_with_empty_messages(self, mock_prompt, mock_get_llm):
        """Test extractor handles empty message list."""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "No information"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        mock_prompt.return_value = Mock()

        state = {
            "messages": []
        }

        result = extractor_node(state)

        assert result == {}
        mock_llm.invoke.assert_called_once()

    @patch('apps.agents.transactional.nodes.extractor.get_llm')
    @patch('apps.agents.transactional.nodes.extractor.get_extraction_prompt')
    def test_extractor_builds_messages_correctly(self, mock_prompt, mock_get_llm):
        """Test extractor builds message list with prompt + state messages."""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Test"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        mock_system_prompt = Mock()
        mock_prompt.return_value = mock_system_prompt

        user_msg = HumanMessage(content="Test message")
        state = {
            "messages": [user_msg]
        }

        extractor_node(state)

        # Check that invoke was called with [prompt] + state messages
        call_args = mock_llm.invoke.call_args[0][0]
        assert call_args[0] == mock_system_prompt
        assert call_args[1] == user_msg

    @patch('apps.agents.transactional.nodes.extractor.get_llm')
    @patch('apps.agents.transactional.nodes.extractor.get_extraction_prompt')
    def test_extractor_extracts_phone_with_multiple_digit_groups(self, mock_prompt, mock_get_llm):
        """Test extractor combines multiple digit groups to form phone."""
        mock_llm = Mock()
        mock_response = Mock()
        # Phone number split across multiple matches
        mock_response.content = "Teléfono: 300 123 4567\nMonto: 50000"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        mock_prompt.return_value = Mock()

        state = {
            "messages": [HumanMessage(content="Test")]
        }

        result = extractor_node(state)

        assert result["phone"] == "3001234567"
        assert result["amount"] == 50000
