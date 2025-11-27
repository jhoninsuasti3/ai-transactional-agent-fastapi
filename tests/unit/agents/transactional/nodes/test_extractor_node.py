"""Unit tests for extractor node - Updated for regex-based extraction."""

import pytest
from langchain_core.messages import HumanMessage, AIMessage

from apps.agents.transactional.nodes.extractor import extractor_node


@pytest.mark.unit
class TestExtractorNode:
    """Test suite for regex-based extractor node."""

    def test_extractor_extracts_phone_and_amount(self):
        """Test extractor successfully extracts phone and amount using regex."""
        state = {
            "messages": [
                HumanMessage(content="Quiero enviar 50000 pesos al 3001234567")
            ]
        }

        result = extractor_node(state)

        assert result["phone"] == "3001234567"
        assert result["amount"] == 50000

    def test_extractor_extracts_phone_only(self):
        """Test extractor extracts only phone when amount not present."""
        state = {
            "messages": [HumanMessage(content="Al 3009876543")]
        }

        result = extractor_node(state)

        assert result["phone"] == "3009876543"
        assert "amount" not in result

    def test_extractor_extracts_amount_only(self):
        """Test extractor extracts only amount when phone not present."""
        state = {
            "messages": [HumanMessage(content="75000 pesos")]
        }

        result = extractor_node(state)

        assert "phone" not in result
        assert result["amount"] == 75000

    def test_extractor_returns_empty_when_nothing_found(self):
        """Test extractor returns empty dict when nothing extracted."""
        state = {
            "messages": [HumanMessage(content="Hola, ¿cómo estás?")]
        }

        result = extractor_node(state)

        assert result == {}

    def test_extractor_extracts_amount_with_dollar_sign(self):
        """Test extractor handles amount with $ prefix."""
        state = {
            "messages": [HumanMessage(content="Enviar $10,000 al 3001112233")]
        }

        result = extractor_node(state)

        assert result["phone"] == "3001112233"
        assert result["amount"] == 10000

    def test_extractor_ignores_invalid_phone_length(self):
        """Test extractor ignores phone numbers that aren't 10 digits."""
        state = {
            "messages": [HumanMessage(content="Enviar 50000 pesos al 300123")]  # Only 6 digits
        }

        result = extractor_node(state)

        assert "phone" not in result
        assert result["amount"] == 50000

    def test_extractor_ignores_phone_not_starting_with_3(self):
        """Test extractor ignores phone numbers not starting with 3."""
        state = {
            "messages": [HumanMessage(content="Enviar 50000 pesos al 5001234567")]
        }

        result = extractor_node(state)

        assert "phone" not in result
        assert result["amount"] == 50000

    def test_extractor_handles_amount_with_commas(self):
        """Test extractor handles amounts with comma separators."""
        state = {
            "messages": [HumanMessage(content="Enviar $50,000 pesos al 3001234567")]
        }

        result = extractor_node(state)

        assert result["phone"] == "3001234567"
        assert result["amount"] == 50000

    def test_extractor_handles_multiple_messages(self):
        """Test extractor searches through multiple messages."""
        state = {
            "messages": [
                HumanMessage(content="Quiero enviar dinero"),
                AIMessage(content="¿A qué número?"),
                HumanMessage(content="Al 3001234567"),
                AIMessage(content="¿Cuánto deseas enviar?"),
                HumanMessage(content="75000 pesos")
            ]
        }

        result = extractor_node(state)

        assert result["phone"] == "3001234567"
        assert result["amount"] == 75000

    def test_extractor_with_empty_messages(self):
        """Test extractor handles empty message list."""
        state = {
            "messages": []
        }

        result = extractor_node(state)

        assert result == {}

    def test_extractor_extracts_phone_from_middle_of_text(self):
        """Test extractor finds phone number in middle of longer text."""
        state = {
            "messages": [
                HumanMessage(content="Por favor envía al número 3009876543 lo antes posible")
            ]
        }

        result = extractor_node(state)

        assert result["phone"] == "3009876543"

    def test_extractor_handles_amount_with_monto_keyword(self):
        """Test extractor finds amount with 'monto:' prefix."""
        state = {
            "messages": [HumanMessage(content="monto: 100000, número 3001234567")]
        }

        result = extractor_node(state)

        assert result["phone"] == "3001234567"
        assert result["amount"] == 100000

    def test_extractor_handles_enviar_keyword(self):
        """Test extractor finds amount with 'envía' keyword."""
        state = {
            "messages": [HumanMessage(content="envía 25,000 al 3005555555")]
        }

        result = extractor_node(state)

        assert result["phone"] == "3005555555"
        assert result["amount"] == 25000

    def test_extractor_handles_transferir_keyword(self):
        """Test extractor finds amount with 'transferir' keyword."""
        state = {
            "messages": [HumanMessage(content="transferir 33,000 al número 3007777777")]
        }

        result = extractor_node(state)

        assert result["phone"] == "3007777777"
        assert result["amount"] == 33000

    def test_extractor_takes_first_match_for_phone(self):
        """Test extractor uses first phone number found."""
        state = {
            "messages": [
                HumanMessage(content="Al 3001111111 o al 3002222222")
            ]
        }

        result = extractor_node(state)

        # Should take first match
        assert result["phone"] == "3001111111"

    def test_extractor_takes_first_match_for_amount(self):
        """Test extractor uses first amount found."""
        state = {
            "messages": [
                HumanMessage(content="50000 pesos o 75000 pesos")
            ]
        }

        result = extractor_node(state)

        # Should take first match
        assert result["amount"] == 50000

    def test_extractor_handles_message_with_list_content(self):
        """Test extractor handles messages with list content."""
        mock_message = HumanMessage(content=["Enviar", "50000", "pesos", "al", "3001234567"])
        state = {
            "messages": [mock_message]
        }

        result = extractor_node(state)

        assert result["phone"] == "3001234567"
        assert result["amount"] == 50000

    def test_extractor_handles_non_string_content(self):
        """Test extractor handles message content that isn't string."""
        class CustomContent:
            def __str__(self):
                return "Enviar 40000 pesos al 3009999999"

        mock_message = type('MockMessage', (), {
            'content': CustomContent()
        })()

        state = {
            "messages": [mock_message]
        }

        result = extractor_node(state)

        assert result["phone"] == "3009999999"
        assert result["amount"] == 40000

    def test_extractor_case_insensitive_keywords(self):
        """Test extractor handles keywords in different cases."""
        state = {
            "messages": [
                HumanMessage(content="ENVIAR 60000 PESOS al 3008888888")
            ]
        }

        result = extractor_node(state)

        assert result["phone"] == "3008888888"
        assert result["amount"] == 60000

    def test_extractor_only_extracts_10_digit_phones(self):
        """Test extractor only accepts exactly 10 digit phone numbers."""
        state = {
            "messages": [
                HumanMessage(content="Números: 300123456 y 30012345678 y 3001234567")
            ]
        }

        result = extractor_node(state)

        # Should only match the 10-digit number
        assert result["phone"] == "3001234567"

    def test_extractor_converts_amount_to_float(self):
        """Test extractor returns amount as float."""
        state = {
            "messages": [HumanMessage(content="50000 pesos")]
        }

        result = extractor_node(state)

        assert isinstance(result["amount"], float)
        assert result["amount"] == 50000.0
