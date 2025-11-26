"""Unit tests for intent routing."""

import pytest

from apps.agents.transactional.routes.intent.route import intent_route


@pytest.mark.unit
class TestIntentRoute:
    """Test suite for intent routing logic."""

    def test_route_transaction_intent(self):
        """Test routing with transaction intent."""
        state = {"intent": "transaction"}
        result = intent_route(state)
        assert result == "transaction"

    def test_route_conversation_intent(self):
        """Test routing with conversation intent."""
        state = {"intent": "conversation"}
        result = intent_route(state)
        assert result == "conversation"

    def test_route_default_to_conversation(self):
        """Test default routing to conversation."""
        state = {}
        result = intent_route(state)
        assert result == "conversation"

    def test_route_unknown_intent_defaults_to_conversation(self):
        """Test unknown intent defaults to conversation."""
        state = {"intent": "unknown_intent"}
        result = intent_route(state)
        assert result == "conversation"

    def test_route_with_extra_state_fields(self):
        """Test routing works with extra state fields."""
        state = {
            "intent": "transaction",
            "phone": "3001234567",
            "amount": 50000,
            "messages": []
        }
        result = intent_route(state)
        assert result == "transaction"
