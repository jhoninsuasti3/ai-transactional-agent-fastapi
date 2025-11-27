"""Unit tests for conversation node - Updated after removing tool binding."""

from unittest.mock import Mock, patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from apps.agents.transactional.nodes.conversation import conversation_node


@pytest.mark.unit
class TestConversationNode:
    """Test suite for conversation node - No tools, purely conversational."""

    @patch("apps.agents.transactional.nodes.conversation.get_llm")
    @patch("apps.agents.transactional.nodes.conversation.get_conversation_prompt")
    def test_conversation_node_generates_response(self, mock_prompt, mock_get_llm):
        """Test conversation node generates conversational response without tools."""
        # Setup mocks
        mock_llm = Mock()
        mock_response = AIMessage(content="¿A qué número deseas enviar?")

        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        mock_prompt.return_value = Mock()

        # Create state
        state = {
            "messages": [HumanMessage(content="Quiero enviar dinero")],
            "phone": None,
            "amount": None,
        }

        # Execute
        result = conversation_node(state)

        # Assert
        assert "messages" in result
        assert len(result["messages"]) == 1
        assert result["messages"][0] == mock_response
        mock_get_llm.assert_called_once()
        # Should NOT call bind_tools anymore
        assert not hasattr(mock_llm, "bind_tools") or not mock_llm.bind_tools.called

    @patch("apps.agents.transactional.nodes.conversation.get_llm")
    @patch("apps.agents.transactional.nodes.conversation.get_conversation_prompt")
    def test_conversation_node_uses_phone_in_prompt(self, mock_prompt, mock_get_llm):
        """Test conversation node passes phone to prompt."""
        mock_llm = Mock()
        mock_response = AIMessage(content="Perfecto, ¿cuánto deseas enviar?")

        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        mock_prompt.return_value = Mock()

        state = {
            "messages": [HumanMessage(content="Al 3001234567")],
            "phone": "3001234567",
            "amount": None,
        }

        conversation_node(state)

        # Verify prompt was called with phone
        mock_prompt.assert_called_once_with(phone="3001234567", amount=None)

    @patch("apps.agents.transactional.nodes.conversation.get_llm")
    @patch("apps.agents.transactional.nodes.conversation.get_conversation_prompt")
    def test_conversation_node_uses_amount_in_prompt(self, mock_prompt, mock_get_llm):
        """Test conversation node passes amount to prompt."""
        mock_llm = Mock()
        mock_response = AIMessage(content="Confirma el envío")

        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        mock_prompt.return_value = Mock()

        state = {
            "messages": [HumanMessage(content="50000 pesos")],
            "phone": "3001234567",
            "amount": 50000,
        }

        conversation_node(state)

        # Verify prompt was called with both phone and amount
        mock_prompt.assert_called_once_with(phone="3001234567", amount=50000)

    @patch("apps.agents.transactional.nodes.conversation.get_llm")
    @patch("apps.agents.transactional.nodes.conversation.get_conversation_prompt")
    def test_conversation_node_no_longer_binds_tools(self, mock_prompt, mock_get_llm):
        """Test conversation node does NOT bind tools (removed for fix)."""
        mock_llm = Mock()
        mock_response = AIMessage(content="Test")

        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        mock_prompt.return_value = Mock()

        state = {"messages": [], "phone": None, "amount": None}

        conversation_node(state)

        # Verify tools were NOT bound (this is the fix for tool_use error)
        assert not hasattr(mock_llm, "bind_tools") or not mock_llm.bind_tools.called

    @patch("apps.agents.transactional.nodes.conversation.get_llm")
    @patch("apps.agents.transactional.nodes.conversation.get_conversation_prompt")
    def test_conversation_node_builds_messages_correctly(self, mock_prompt, mock_get_llm):
        """Test conversation node builds message list correctly."""
        mock_llm = Mock()
        mock_response = AIMessage(content="Response")

        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        mock_system_prompt = Mock()
        mock_prompt.return_value = mock_system_prompt

        user_msg1 = HumanMessage(content="First")
        user_msg2 = HumanMessage(content="Second")
        state = {"messages": [user_msg1, user_msg2], "phone": None, "amount": None}

        conversation_node(state)

        # Check that invoke was called with [prompt] + state messages
        call_args = mock_llm.invoke.call_args[0][0]
        assert call_args[0] == mock_system_prompt
        assert call_args[1] == user_msg1
        assert call_args[2] == user_msg2

    @patch("apps.agents.transactional.nodes.conversation.get_llm")
    @patch("apps.agents.transactional.nodes.conversation.get_conversation_prompt")
    def test_conversation_node_with_empty_messages(self, mock_prompt, mock_get_llm):
        """Test conversation node with empty message list."""
        mock_llm = Mock()
        mock_response = AIMessage(content="¡Hola! ¿En qué puedo ayudarte?")

        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        mock_prompt.return_value = Mock()

        state = {"messages": [], "phone": None, "amount": None}

        result = conversation_node(state)

        assert len(result["messages"]) == 1
        assert result["messages"][0].content == "¡Hola! ¿En qué puedo ayudarte?"

    @patch("apps.agents.transactional.nodes.conversation.get_llm")
    @patch("apps.agents.transactional.nodes.conversation.get_conversation_prompt")
    def test_conversation_node_with_no_response_content(self, mock_prompt, mock_get_llm):
        """Test conversation node when response has no content."""
        mock_llm = Mock()
        mock_response = AIMessage(content="")

        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        mock_prompt.return_value = Mock()

        state = {"messages": [HumanMessage(content="Test")], "phone": None, "amount": None}

        result = conversation_node(state)

        assert result["messages"][0] == mock_response

    @patch("apps.agents.transactional.nodes.conversation.get_llm")
    @patch("apps.agents.transactional.nodes.conversation.get_conversation_prompt")
    def test_conversation_node_calls_llm_with_default_temperature(self, mock_prompt, mock_get_llm):
        """Test conversation node calls get_llm without temperature parameter."""
        mock_llm = Mock()
        mock_response = AIMessage(content="Test")

        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        mock_prompt.return_value = Mock()

        state = {"messages": [], "phone": None, "amount": None}

        conversation_node(state)

        # Should be called without temperature argument (uses default)
        mock_get_llm.assert_called_once_with()

    @patch("apps.agents.transactional.nodes.conversation.get_llm")
    @patch("apps.agents.transactional.nodes.conversation.get_conversation_prompt")
    def test_conversation_node_with_both_phone_and_amount(self, mock_prompt, mock_get_llm):
        """Test conversation node when both phone and amount are present."""
        mock_llm = Mock()
        mock_response = AIMessage(content="Perfecto, ¿deseas confirmar?")

        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        mock_prompt.return_value = Mock()

        state = {"messages": [HumanMessage(content="Sí")], "phone": "3001234567", "amount": 75000}

        result = conversation_node(state)

        # Verify prompt was called with both
        mock_prompt.assert_called_once_with(phone="3001234567", amount=75000)

        assert result["messages"][0].content == "Perfecto, ¿deseas confirmar?"

    @patch("apps.agents.transactional.nodes.conversation.get_llm")
    @patch("apps.agents.transactional.nodes.conversation.get_conversation_prompt")
    def test_conversation_node_purely_conversational(self, mock_prompt, mock_get_llm):
        """Test that conversation node is purely conversational without tool execution logic."""
        mock_llm = Mock()
        mock_response = AIMessage(content="Response text")

        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        mock_prompt.return_value = Mock()

        state = {"messages": [HumanMessage(content="Test message")], "phone": None, "amount": None}

        result = conversation_node(state)

        # Should only return messages, no tool execution
        assert "messages" in result
        assert len(result) == 1  # Only "messages" key
        assert isinstance(result["messages"][0], AIMessage)
