"""Unit tests for validation routing."""

import pytest

from apps.agents.transactional.routes.validation.route import validation_route


@pytest.mark.unit
class TestValidationRoute:
    """Test suite for validation routing logic."""

    def test_route_valid_transaction(self):
        """Test routing when transaction is valid."""
        state = {"is_valid": True}
        result = validation_route(state)
        assert result == "valid"

    def test_route_invalid_transaction(self):
        """Test routing when transaction is invalid."""
        state = {"is_valid": False}
        result = validation_route(state)
        assert result == "invalid"

    def test_route_default_to_invalid(self):
        """Test default routing when is_valid not in state."""
        state = {}
        result = validation_route(state)
        assert result == "invalid"

    def test_route_with_extra_state_fields(self):
        """Test routing works with extra state fields."""
        state = {
            "is_valid": True,
            "validation_id": "VAL-123",
            "phone": "3001234567",
            "amount": 50000,
        }
        result = validation_route(state)
        assert result == "valid"

    def test_route_with_validation_message(self):
        """Test routing with validation message."""
        state = {"is_valid": False, "validation_message": "Insufficient funds"}
        result = validation_route(state)
        assert result == "invalid"
