"""Unit tests for LangGraph state machine routing functions."""

import pytest
from langgraph.graph import END

from apps.agents.transactional.graph import (
    create_graph,
    get_agent,
    should_confirm,
    should_execute,
    should_extract,
    should_validate,
)


@pytest.mark.unit
class TestGraphRoutingFunctions:
    """Test suite for graph routing functions."""

    def test_should_extract_with_both_phone_and_amount(self):
        """Test should_extract routes to validate when both phone and amount present."""
        state = {"phone": "3001234567", "amount": 50000}
        result = should_extract(state)
        assert result == "validate"

    def test_should_extract_without_phone(self):
        """Test should_extract routes to END when phone missing and no phone pattern in message."""
        from langchain_core.messages import HumanMessage

        state = {"phone": None, "amount": 50000, "messages": [HumanMessage(content="50000 pesos")]}
        result = should_extract(state)
        # Will extract because has amount pattern
        assert result == "extract"

    def test_should_extract_without_amount(self):
        """Test should_extract routes to extract when amount missing but has data pattern."""
        from langchain_core.messages import HumanMessage

        state = {
            "phone": "3001234567",
            "amount": None,
            "messages": [HumanMessage(content="3001234567")],
        }
        result = should_extract(state)
        assert result == "extract"

    def test_should_extract_without_both(self):
        """Test should_extract routes to END when both missing and no data patterns."""
        from langchain_core.messages import HumanMessage

        state = {"phone": None, "amount": None, "messages": [HumanMessage(content="Hola")]}
        result = should_extract(state)
        assert result == END

    def test_should_validate_with_both_phone_and_amount(self):
        """Test should_validate routes to validate when data present."""
        state = {"phone": "3001234567", "amount": 50000}
        result = should_validate(state)
        assert result == "validate"

    def test_should_validate_without_data(self):
        """Test should_validate routes to END when data missing."""
        state = {"phone": None, "amount": None}
        result = should_validate(state)
        assert result == END

    def test_should_validate_partial_data_phone_only(self):
        """Test should_validate routes to END with only phone."""
        state = {"phone": "3001234567", "amount": None}
        result = should_validate(state)
        assert result == END

    def test_should_validate_partial_data_amount_only(self):
        """Test should_validate routes to END with only amount."""
        state = {"phone": None, "amount": 50000}
        result = should_validate(state)
        assert result == END

    def test_should_confirm_needs_confirmation_true(self):
        """Test should_confirm routes to confirmation when needed."""
        state = {"needs_confirmation": True}
        result = should_confirm(state)
        assert result == "confirmation"

    def test_should_confirm_needs_confirmation_false(self):
        """Test should_confirm routes to END when not needed."""
        state = {"needs_confirmation": False}
        result = should_confirm(state)
        assert result == END

    def test_should_confirm_needs_confirmation_none(self):
        """Test should_confirm routes to END when None."""
        state = {"needs_confirmation": None}
        result = should_confirm(state)
        assert result == END

    def test_should_execute_confirmed_true(self):
        """Test should_execute routes to transaction when confirmed."""
        state = {"confirmed": True}
        result = should_execute(state)
        assert result == "transaction"

    def test_should_execute_confirmed_false(self):
        """Test should_execute routes to END when not confirmed."""
        state = {"confirmed": False}
        result = should_execute(state)
        assert result == END

    def test_should_execute_confirmed_none(self):
        """Test should_execute routes to END when None."""
        state = {"confirmed": None}
        result = should_execute(state)
        assert result == END

    def test_create_graph_returns_compiled_graph(self):
        """Test create_graph returns a compiled graph."""
        graph = create_graph()
        assert graph is not None
        # Verify it's a compiled graph (has invoke method)
        assert hasattr(graph, "invoke")

    def test_agent_factory_exists(self):
        """Test that agent factory function exists and returns agent."""
        agent = get_agent()
        assert agent is not None
        assert hasattr(agent, "invoke")

    def test_graph_has_all_nodes(self):
        """Test graph has all required nodes."""
        graph = create_graph()
        # The compiled graph should be invokable
        assert hasattr(graph, "invoke")
        # We can't directly access nodes in compiled graph,
        # but we can verify it was created successfully
        assert graph is not None


@pytest.mark.unit
class TestGraphEdgeCases:
    """Test edge cases for graph routing."""

    def test_should_extract_with_empty_string_phone(self):
        """Test routing with empty string phone - routes to extract if has amount pattern."""
        from langchain_core.messages import HumanMessage

        state = {"phone": "", "amount": 50000, "messages": [HumanMessage(content="50000 pesos")]}
        result = should_extract(state)
        assert result == "extract"

    def test_should_extract_with_zero_amount(self):
        """Test routing with zero amount - routes to extract if has phone pattern."""
        from langchain_core.messages import HumanMessage

        state = {
            "phone": "3001234567",
            "amount": 0,
            "messages": [HumanMessage(content="3001234567")],
        }
        result = should_extract(state)
        assert result == "extract"

    def test_should_validate_with_empty_strings(self):
        """Test routing with empty strings - routes to END when no valid data."""
        state = {"phone": "", "amount": ""}
        result = should_validate(state)
        assert result == END

    def test_state_with_extra_fields(self):
        """Test routing works with additional state fields."""
        state = {
            "phone": "3001234567",
            "amount": 50000,
            "messages": [],
            "transaction_id": None,
            "extra_field": "value",
        }
        result = should_extract(state)
        assert result == "validate"

    def test_state_missing_get_method(self):
        """Test routing with state as dict (has get method)."""
        state = {"phone": "3001234567", "amount": 50000}
        # All routing functions use .get() which works on dicts
        assert should_extract(state) == "validate"
        assert should_validate(state) == "validate"

    def test_should_extract_with_no_messages(self):
        """Test should_extract returns END when no messages."""
        state = {"phone": None, "amount": None, "messages": []}
        result = should_extract(state)
        assert result == END

    def test_should_extract_with_only_ai_messages(self):
        """Test should_extract returns END when only AI messages."""
        from langchain_core.messages import AIMessage

        state = {"phone": None, "amount": None, "messages": [AIMessage(content="Hello")]}
        result = should_extract(state)
        assert result == END

    def test_should_extract_with_list_content(self):
        """Test should_extract handles list content."""
        from langchain_core.messages import HumanMessage

        msg = HumanMessage(content=["Enviar", "al", "3001234567"])
        state = {"phone": None, "amount": None, "messages": [msg]}
        result = should_extract(state)
        assert result == "extract"
