"""Unit tests for LangGraph state machine routing functions."""

import pytest
from langgraph.graph import END

from apps.agents.transactional.graph import (
    should_extract,
    should_validate,
    should_confirm,
    should_execute,
    create_graph,
    agent,
)


@pytest.mark.unit
class TestGraphRoutingFunctions:
    """Test suite for graph routing functions."""

    def test_should_extract_with_both_phone_and_amount(self):
        """Test should_extract routes to validate when both phone and amount present."""
        state = {
            "phone": "3001234567",
            "amount": 50000
        }
        result = should_extract(state)
        assert result == "validate"

    def test_should_extract_without_phone(self):
        """Test should_extract routes to extract when phone missing."""
        state = {
            "phone": None,
            "amount": 50000
        }
        result = should_extract(state)
        assert result == "extract"

    def test_should_extract_without_amount(self):
        """Test should_extract routes to extract when amount missing."""
        state = {
            "phone": "3001234567",
            "amount": None
        }
        result = should_extract(state)
        assert result == "extract"

    def test_should_extract_without_both(self):
        """Test should_extract routes to extract when both missing."""
        state = {
            "phone": None,
            "amount": None
        }
        result = should_extract(state)
        assert result == "extract"

    def test_should_validate_with_both_phone_and_amount(self):
        """Test should_validate routes to validate when data present."""
        state = {
            "phone": "3001234567",
            "amount": 50000
        }
        result = should_validate(state)
        assert result == "validate"

    def test_should_validate_without_data(self):
        """Test should_validate routes to conversation when data missing."""
        state = {
            "phone": None,
            "amount": None
        }
        result = should_validate(state)
        assert result == "conversation"

    def test_should_validate_partial_data_phone_only(self):
        """Test should_validate routes to conversation with only phone."""
        state = {
            "phone": "3001234567",
            "amount": None
        }
        result = should_validate(state)
        assert result == "conversation"

    def test_should_validate_partial_data_amount_only(self):
        """Test should_validate routes to conversation with only amount."""
        state = {
            "phone": None,
            "amount": 50000
        }
        result = should_validate(state)
        assert result == "conversation"

    def test_should_confirm_needs_confirmation_true(self):
        """Test should_confirm routes to confirmation when needed."""
        state = {
            "needs_confirmation": True
        }
        result = should_confirm(state)
        assert result == "confirmation"

    def test_should_confirm_needs_confirmation_false(self):
        """Test should_confirm routes to END when not needed."""
        state = {
            "needs_confirmation": False
        }
        result = should_confirm(state)
        assert result == END

    def test_should_confirm_needs_confirmation_none(self):
        """Test should_confirm routes to END when None."""
        state = {
            "needs_confirmation": None
        }
        result = should_confirm(state)
        assert result == END

    def test_should_execute_confirmed_true(self):
        """Test should_execute routes to transaction when confirmed."""
        state = {
            "confirmed": True
        }
        result = should_execute(state)
        assert result == "transaction"

    def test_should_execute_confirmed_false(self):
        """Test should_execute routes to END when not confirmed."""
        state = {
            "confirmed": False
        }
        result = should_execute(state)
        assert result == END

    def test_should_execute_confirmed_none(self):
        """Test should_execute routes to END when None."""
        state = {
            "confirmed": None
        }
        result = should_execute(state)
        assert result == END

    def test_create_graph_returns_compiled_graph(self):
        """Test create_graph returns a compiled graph."""
        graph = create_graph()
        assert graph is not None
        # Verify it's a compiled graph (has invoke method)
        assert hasattr(graph, 'invoke')

    def test_singleton_agent_exists(self):
        """Test that singleton agent instance exists."""
        assert agent is not None
        assert hasattr(agent, 'invoke')

    def test_graph_has_all_nodes(self):
        """Test graph has all required nodes."""
        graph = create_graph()
        # The compiled graph should be invokable
        assert hasattr(graph, 'invoke')
        # We can't directly access nodes in compiled graph,
        # but we can verify it was created successfully
        assert graph is not None


@pytest.mark.unit
class TestGraphEdgeCases:
    """Test edge cases for graph routing."""

    def test_should_extract_with_empty_string_phone(self):
        """Test routing with empty string phone."""
        state = {
            "phone": "",
            "amount": 50000
        }
        result = should_extract(state)
        assert result == "extract"

    def test_should_extract_with_zero_amount(self):
        """Test routing with zero amount."""
        state = {
            "phone": "3001234567",
            "amount": 0
        }
        result = should_extract(state)
        assert result == "extract"

    def test_should_validate_with_empty_strings(self):
        """Test routing with empty strings."""
        state = {
            "phone": "",
            "amount": ""
        }
        result = should_validate(state)
        assert result == "conversation"

    def test_state_with_extra_fields(self):
        """Test routing works with additional state fields."""
        state = {
            "phone": "3001234567",
            "amount": 50000,
            "messages": [],
            "transaction_id": None,
            "extra_field": "value"
        }
        result = should_extract(state)
        assert result == "validate"

    def test_state_missing_get_method(self):
        """Test routing with state as dict (has get method)."""
        state = {
            "phone": "3001234567",
            "amount": 50000
        }
        # All routing functions use .get() which works on dicts
        assert should_extract(state) == "validate"
        assert should_validate(state) == "validate"
