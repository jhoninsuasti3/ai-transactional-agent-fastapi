"""Unit tests for transaction node."""

from unittest.mock import patch

import pytest

from apps.agents.transactional.nodes.transaction import transaction_node
from apps.agents.transactional.state import TransactionalState


@pytest.mark.unit
class TestTransactionNode:
    """Test suite for transaction_node."""

    @patch("apps.agents.transactional.nodes.transaction.execute_transaction_tool")
    def test_successful_transaction(self, mock_tool):
        """Test successful transaction execution."""
        mock_tool.invoke.return_value = {
            "success": True,
            "transaction_id": "TXN-12345",
            "status": "completed",
            "message": "Transaction completed successfully",
        }

        state: TransactionalState = {
            "messages": [],
            "phone": "3001234567",
            "amount": 50000,
            "validation_id": "VAL-123",
            "needs_confirmation": False,
            "confirmed": True,
            "transaction_id": None,
            "transaction_status": None,
        }

        result = transaction_node(state)

        assert result["transaction_id"] == "TXN-12345"
        assert result["transaction_status"] == "completed"
        assert len(result["messages"]) == 1
        mock_tool.invoke.assert_called_once_with(
            {"phone": "3001234567", "amount": 50000, "validation_id": "VAL-123"}
        )

    @patch("apps.agents.transactional.nodes.transaction.execute_transaction_tool")
    def test_failed_transaction(self, mock_tool):
        """Test failed transaction execution."""
        mock_tool.invoke.return_value = {
            "success": False,
            "status": "failed",
            "error": "Insufficient funds",
        }

        state: TransactionalState = {
            "messages": [],
            "phone": "3001234567",
            "amount": 50000,
            "validation_id": "VAL-123",
            "needs_confirmation": False,
            "confirmed": True,
            "transaction_id": None,
            "transaction_status": None,
        }

        result = transaction_node(state)

        assert result["transaction_status"] == "failed"
        assert len(result["messages"]) == 1

    @patch("apps.agents.transactional.nodes.transaction.execute_transaction_tool")
    def test_missing_phone(self, mock_tool):
        """Test transaction with missing phone."""
        state: TransactionalState = {
            "messages": [],
            "phone": None,
            "amount": 50000,
            "validation_id": "VAL-123",
            "needs_confirmation": False,
            "confirmed": True,
            "transaction_id": None,
            "transaction_status": None,
        }

        result = transaction_node(state)

        assert result["transaction_status"] == "failed"
        assert len(result["messages"]) == 1
        assert "Error" in result["messages"][0].content
        mock_tool.invoke.assert_not_called()

    @patch("apps.agents.transactional.nodes.transaction.execute_transaction_tool")
    def test_missing_amount(self, mock_tool):
        """Test transaction with missing amount."""
        state: TransactionalState = {
            "messages": [],
            "phone": "3001234567",
            "amount": None,
            "validation_id": "VAL-123",
            "needs_confirmation": False,
            "confirmed": True,
            "transaction_id": None,
            "transaction_status": None,
        }

        result = transaction_node(state)

        assert result["transaction_status"] == "failed"
        assert len(result["messages"]) == 1
        mock_tool.invoke.assert_not_called()

    @patch("apps.agents.transactional.nodes.transaction.execute_transaction_tool")
    def test_transaction_without_validation_id(self, mock_tool):
        """Test transaction without validation ID."""
        mock_tool.invoke.return_value = {
            "success": True,
            "transaction_id": "TXN-99999",
            "status": "completed",
        }

        state: TransactionalState = {
            "messages": [],
            "phone": "3001234567",
            "amount": 50000,
            "validation_id": None,
            "needs_confirmation": False,
            "confirmed": True,
            "transaction_id": None,
            "transaction_status": None,
        }

        result = transaction_node(state)

        assert result["transaction_id"] == "TXN-99999"
        assert result["transaction_status"] == "completed"
        mock_tool.invoke.assert_called_once_with(
            {"phone": "3001234567", "amount": 50000, "validation_id": None}
        )

    @patch("apps.agents.transactional.nodes.transaction.execute_transaction_tool")
    def test_transaction_pending_status(self, mock_tool):
        """Test transaction with pending status."""
        mock_tool.invoke.return_value = {
            "success": True,
            "transaction_id": "TXN-88888",
            "status": "pending",
            "message": "Transaction is being processed",
        }

        state: TransactionalState = {
            "messages": [],
            "phone": "3001234567",
            "amount": 50000,
            "validation_id": "VAL-123",
            "needs_confirmation": False,
            "confirmed": True,
            "transaction_id": None,
            "transaction_status": None,
        }

        result = transaction_node(state)

        assert result["transaction_id"] == "TXN-88888"
        assert result["transaction_status"] == "pending"
