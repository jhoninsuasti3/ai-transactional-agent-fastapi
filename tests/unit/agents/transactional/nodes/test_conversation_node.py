"""Unit tests for conversation node."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage

from apps.agents.transactional.nodes.conversation import conversation_node


@pytest.mark.unit
class TestConversationNode:
    """Test suite for conversation node."""

    @patch('apps.agents.transactional.nodes.conversation.get_llm')
    @patch('apps.agents.transactional.nodes.conversation.get_conversation_prompt')
    @patch('apps.agents.transactional.nodes.conversation.format_phone_number_tool')
    def test_conversation_node_generates_response(self, mock_tool, mock_prompt, mock_get_llm):
        """Test conversation node generates conversational response."""
        # Setup mocks
        mock_llm = Mock()
        mock_llm_with_tools = Mock()
        mock_response = AIMessage(content="¿A qué número deseas enviar?")
        mock_response.tool_calls = []

        mock_llm.bind_tools.return_value = mock_llm_with_tools
        mock_llm_with_tools.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        mock_prompt.return_value = Mock()

        # Create state
        state = {
            "messages": [HumanMessage(content="Quiero enviar dinero")],
            "phone": None,
            "amount": None
        }

        # Execute
        result = conversation_node(state)

        # Assert
        assert "messages" in result
        assert len(result["messages"]) == 1
        assert result["messages"][0] == mock_response
        mock_get_llm.assert_called_once()
        mock_llm.bind_tools.assert_called_once()

    @patch('apps.agents.transactional.nodes.conversation.get_llm')
    @patch('apps.agents.transactional.nodes.conversation.get_conversation_prompt')
    @patch('apps.agents.transactional.nodes.conversation.format_phone_number_tool')
    def test_conversation_node_uses_phone_in_prompt(self, mock_tool, mock_prompt, mock_get_llm):
        """Test conversation node passes phone to prompt."""
        mock_llm = Mock()
        mock_llm_with_tools = Mock()
        mock_response = AIMessage(content="Perfecto, ¿cuánto deseas enviar?")
        mock_response.tool_calls = []

        mock_llm.bind_tools.return_value = mock_llm_with_tools
        mock_llm_with_tools.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        mock_prompt.return_value = Mock()

        state = {
            "messages": [HumanMessage(content="Al 3001234567")],
            "phone": "3001234567",
            "amount": None
        }

        conversation_node(state)

        # Verify prompt was called with phone
        mock_prompt.assert_called_once_with(
            phone="3001234567",
            amount=None
        )

    @patch('apps.agents.transactional.nodes.conversation.get_llm')
    @patch('apps.agents.transactional.nodes.conversation.get_conversation_prompt')
    @patch('apps.agents.transactional.nodes.conversation.format_phone_number_tool')
    def test_conversation_node_uses_amount_in_prompt(self, mock_tool, mock_prompt, mock_get_llm):
        """Test conversation node passes amount to prompt."""
        mock_llm = Mock()
        mock_llm_with_tools = Mock()
        mock_response = AIMessage(content="Confirma el envío")
        mock_response.tool_calls = []

        mock_llm.bind_tools.return_value = mock_llm_with_tools
        mock_llm_with_tools.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        mock_prompt.return_value = Mock()

        state = {
            "messages": [HumanMessage(content="50000 pesos")],
            "phone": "3001234567",
            "amount": 50000
        }

        conversation_node(state)

        # Verify prompt was called with both phone and amount
        mock_prompt.assert_called_once_with(
            phone="3001234567",
            amount=50000
        )

    @patch('apps.agents.transactional.nodes.conversation.get_llm')
    @patch('apps.agents.transactional.nodes.conversation.get_conversation_prompt')
    @patch('apps.agents.transactional.nodes.conversation.format_phone_number_tool')
    def test_conversation_node_binds_tools(self, mock_tool, mock_prompt, mock_get_llm):
        """Test conversation node binds format_phone_number_tool."""
        mock_llm = Mock()
        mock_llm_with_tools = Mock()
        mock_response = AIMessage(content="Test")
        mock_response.tool_calls = []

        mock_llm.bind_tools.return_value = mock_llm_with_tools
        mock_llm_with_tools.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        mock_prompt.return_value = Mock()

        state = {
            "messages": [],
            "phone": None,
            "amount": None
        }

        conversation_node(state)

        # Verify tools were bound
        mock_llm.bind_tools.assert_called_once_with([mock_tool])

    @patch('apps.agents.transactional.nodes.conversation.get_llm')
    @patch('apps.agents.transactional.nodes.conversation.get_conversation_prompt')
    @patch('apps.agents.transactional.nodes.conversation.format_phone_number_tool')
    def test_conversation_node_handles_tool_calls(self, mock_tool, mock_prompt, mock_get_llm):
        """Test conversation node handles response with tool calls."""
        mock_llm = Mock()
        mock_llm_with_tools = Mock()
        mock_response = AIMessage(content="Formatting phone")
        mock_response.tool_calls = [{"name": "format_phone_number", "args": {}}]

        mock_llm.bind_tools.return_value = mock_llm_with_tools
        mock_llm_with_tools.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        mock_prompt.return_value = Mock()

        state = {
            "messages": [HumanMessage(content="300-123-4567")],
            "phone": None,
            "amount": None
        }

        result = conversation_node(state)

        assert result["messages"][0] == mock_response
        assert len(mock_response.tool_calls) > 0

    @patch('apps.agents.transactional.nodes.conversation.get_llm')
    @patch('apps.agents.transactional.nodes.conversation.get_conversation_prompt')
    @patch('apps.agents.transactional.nodes.conversation.format_phone_number_tool')
    def test_conversation_node_builds_messages_correctly(self, mock_tool, mock_prompt, mock_get_llm):
        """Test conversation node builds message list correctly."""
        mock_llm = Mock()
        mock_llm_with_tools = Mock()
        mock_response = AIMessage(content="Response")
        mock_response.tool_calls = []

        mock_llm.bind_tools.return_value = mock_llm_with_tools
        mock_llm_with_tools.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        mock_system_prompt = Mock()
        mock_prompt.return_value = mock_system_prompt

        user_msg1 = HumanMessage(content="First")
        user_msg2 = HumanMessage(content="Second")
        state = {
            "messages": [user_msg1, user_msg2],
            "phone": None,
            "amount": None
        }

        conversation_node(state)

        # Check that invoke was called with [prompt] + state messages
        call_args = mock_llm_with_tools.invoke.call_args[0][0]
        assert call_args[0] == mock_system_prompt
        assert call_args[1] == user_msg1
        assert call_args[2] == user_msg2

    @patch('apps.agents.transactional.nodes.conversation.get_llm')
    @patch('apps.agents.transactional.nodes.conversation.get_conversation_prompt')
    @patch('apps.agents.transactional.nodes.conversation.format_phone_number_tool')
    def test_conversation_node_with_empty_messages(self, mock_tool, mock_prompt, mock_get_llm):
        """Test conversation node with empty message list."""
        mock_llm = Mock()
        mock_llm_with_tools = Mock()
        mock_response = AIMessage(content="¡Hola! ¿En qué puedo ayudarte?")
        mock_response.tool_calls = []

        mock_llm.bind_tools.return_value = mock_llm_with_tools
        mock_llm_with_tools.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        mock_prompt.return_value = Mock()

        state = {
            "messages": [],
            "phone": None,
            "amount": None
        }

        result = conversation_node(state)

        assert len(result["messages"]) == 1
        assert result["messages"][0].content == "¡Hola! ¿En qué puedo ayudarte?"

    @patch('apps.agents.transactional.nodes.conversation.get_llm')
    @patch('apps.agents.transactional.nodes.conversation.get_conversation_prompt')
    @patch('apps.agents.transactional.nodes.conversation.format_phone_number_tool')
    def test_conversation_node_with_no_response_content(self, mock_tool, mock_prompt, mock_get_llm):
        """Test conversation node when response has no content."""
        mock_llm = Mock()
        mock_llm_with_tools = Mock()
        mock_response = AIMessage(content="")
        mock_response.tool_calls = []

        mock_llm.bind_tools.return_value = mock_llm_with_tools
        mock_llm_with_tools.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        mock_prompt.return_value = Mock()

        state = {
            "messages": [HumanMessage(content="Test")],
            "phone": None,
            "amount": None
        }

        result = conversation_node(state)

        assert result["messages"][0] == mock_response

    @patch('apps.agents.transactional.nodes.conversation.get_llm')
    @patch('apps.agents.transactional.nodes.conversation.get_conversation_prompt')
    @patch('apps.agents.transactional.nodes.conversation.format_phone_number_tool')
    def test_conversation_node_calls_llm_with_default_temperature(self, mock_tool, mock_prompt, mock_get_llm):
        """Test conversation node calls get_llm without temperature parameter."""
        mock_llm = Mock()
        mock_llm_with_tools = Mock()
        mock_response = AIMessage(content="Test")
        mock_response.tool_calls = []

        mock_llm.bind_tools.return_value = mock_llm_with_tools
        mock_llm_with_tools.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        mock_prompt.return_value = Mock()

        state = {
            "messages": [],
            "phone": None,
            "amount": None
        }

        conversation_node(state)

        # Should be called without temperature argument (uses default)
        mock_get_llm.assert_called_once_with()
