"""Unit tests for application constants."""

import pytest

from apps.orchestrator.constants import LANGGRAPH_RECURSION_LIMIT


@pytest.mark.unit
class TestConstants:
    """Test suite for application constants."""

    def test_langgraph_recursion_limit_is_integer(self):
        """Test LANGGRAPH_RECURSION_LIMIT is an integer."""
        assert isinstance(LANGGRAPH_RECURSION_LIMIT, int)

    def test_langgraph_recursion_limit_is_positive(self):
        """Test LANGGRAPH_RECURSION_LIMIT is positive."""
        assert LANGGRAPH_RECURSION_LIMIT > 0

    def test_langgraph_recursion_limit_value(self):
        """Test LANGGRAPH_RECURSION_LIMIT has expected value."""
        assert LANGGRAPH_RECURSION_LIMIT == 5
