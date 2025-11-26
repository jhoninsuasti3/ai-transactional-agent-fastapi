"""Unit tests for validator node."""

import pytest
from unittest.mock import patch

from apps.agents.transactional.nodes.validator import validator_node
from apps.agents.transactional.state import TransactionalState


@pytest.mark.unit
class TestValidatorNode:
    """Test suite for validator_node."""

    @patch('apps.agents.transactional.nodes.validator.validate_transaction_tool')
    def test_successful_validation(self, mock_tool):
        """Test successful transaction validation."""
        mock_tool.invoke.return_value = {
            "valid": True,
            "message": "Transaction can be processed",
            "validation_id": "VAL-12345"
        }

        state: TransactionalState = {
            "messages": [],
            "phone": "3001234567",
            "amount": 50000,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        result = validator_node(state)

        assert result["validation_id"] == "VAL-12345"
        assert result["needs_confirmation"] is True
        assert len(result["messages"]) == 1
        mock_tool.invoke.assert_called_once_with({"phone": "3001234567", "amount": 50000})

    @patch('apps.agents.transactional.nodes.validator.validate_transaction_tool')
    def test_failed_validation(self, mock_tool):
        """Test failed transaction validation."""
        mock_tool.invoke.return_value = {
            "valid": False,
            "error": "Insufficient funds"
        }

        state: TransactionalState = {
            "messages": [],
            "phone": "3001234567",
            "amount": 50000,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        result = validator_node(state)

        assert result["needs_confirmation"] is False
        assert len(result["messages"]) == 1
        assert "validation_id" not in result

    @patch('apps.agents.transactional.nodes.validator.validate_transaction_tool')
    def test_missing_phone(self, mock_tool):
        """Test validation with missing phone."""
        state: TransactionalState = {
            "messages": [],
            "phone": None,
            "amount": 50000,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        result = validator_node(state)

        assert result["needs_confirmation"] is False
        assert len(result["messages"]) == 1
        assert "Error" in result["messages"][0].content
        mock_tool.invoke.assert_not_called()

    @patch('apps.agents.transactional.nodes.validator.validate_transaction_tool')
    def test_missing_amount(self, mock_tool):
        """Test validation with missing amount."""
        state: TransactionalState = {
            "messages": [],
            "phone": "3001234567",
            "amount": None,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        result = validator_node(state)

        assert result["needs_confirmation"] is False
        assert len(result["messages"]) == 1
        assert "Error" in result["messages"][0].content
        mock_tool.invoke.assert_not_called()

    @patch('apps.agents.transactional.nodes.validator.validate_transaction_tool')
    def test_missing_both_phone_and_amount(self, mock_tool):
        """Test validation with missing both phone and amount."""
        state: TransactionalState = {
            "messages": [],
            "phone": None,
            "amount": None,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        result = validator_node(state)

        assert result["needs_confirmation"] is False
        assert len(result["messages"]) == 1
        mock_tool.invoke.assert_not_called()

    @patch('apps.agents.transactional.nodes.validator.validate_transaction_tool')
    def test_validation_with_small_amount(self, mock_tool):
        """Test validation with small amount."""
        mock_tool.invoke.return_value = {
            "valid": True,
            "validation_id": "VAL-99999"
        }

        state: TransactionalState = {
            "messages": [],
            "phone": "3001234567",
            "amount": 1000,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        result = validator_node(state)

        assert result["validation_id"] == "VAL-99999"
        assert result["needs_confirmation"] is True
        mock_tool.invoke.assert_called_once_with({"phone": "3001234567", "amount": 1000})

    @patch('apps.agents.transactional.nodes.validator.validate_transaction_tool')
    def test_validation_with_large_amount(self, mock_tool):
        """Test validation with large amount."""
        mock_tool.invoke.return_value = {
            "valid": True,
            "validation_id": "VAL-88888"
        }

        state: TransactionalState = {
            "messages": [],
            "phone": "3001234567",
            "amount": 10000000,
            "needs_confirmation": False,
            "confirmed": False,
            "transaction_id": None,
            "transaction_status": None,
        }

        result = validator_node(state)

        assert result["validation_id"] == "VAL-88888"
        assert result["needs_confirmation"] is True
