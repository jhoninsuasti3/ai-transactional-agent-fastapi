"""Unit tests for transactional agent creation."""

import pytest
from unittest.mock import Mock

from apps.agents.transactional.agent import create_transactional_agent


@pytest.mark.unit
class TestTransactionalAgent:
    """Test suite for transactional agent."""

    def test_create_agent_without_config(self):
        """Test creating agent without config."""
        agent = create_transactional_agent()

        assert agent is not None
        assert hasattr(agent, 'invoke')
        assert hasattr(agent, 'ainvoke')

    def test_create_agent_with_empty_config(self):
        """Test creating agent with empty config dict."""
        agent = create_transactional_agent(config={})

        assert agent is not None
        assert hasattr(agent, 'invoke')

    def test_create_agent_with_checkpointer(self):
        """Test creating agent with checkpointer in config."""
        mock_checkpointer = Mock()

        agent = create_transactional_agent(config={"checkpointer": mock_checkpointer})

        assert agent is not None
        assert hasattr(agent, 'invoke')

    def test_agent_has_all_methods(self):
        """Test that agent graph has all required methods."""
        agent = create_transactional_agent()

        assert agent is not None
        assert hasattr(agent, 'invoke')
        assert hasattr(agent, 'ainvoke')
        assert callable(agent.invoke)
        assert callable(agent.ainvoke)

    def test_create_agent_idempotent(self):
        """Test that creating multiple agents works."""
        agent1 = create_transactional_agent()
        agent2 = create_transactional_agent()

        assert agent1 is not None
        assert agent2 is not None
        # They should be different instances
        assert agent1 is not agent2

    def test_agent_with_custom_config_values(self):
        """Test creating agent with custom config values."""
        config = {
            "checkpointer": Mock(),
            "llm": Mock(),
            "transaction_client": Mock(),
        }

        agent = create_transactional_agent(config=config)

        assert agent is not None
        assert hasattr(agent, 'invoke')
