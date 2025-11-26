"""Tests for get_transaction_status tool."""

import pytest
from unittest.mock import patch

from apps.agents.transactional.tools.get_transaction_status import get_transaction_status_tool


@pytest.mark.unit
class TestGetTransactionStatusTool:
    """Test suite for get_transaction_status_tool."""

    @patch('apps.agents.transactional.tools.get_transaction_status.transaction_client')
    def test_get_completed_transaction_status(self, mock_client):
        """Test getting status of completed transaction."""
        mock_client.get.return_value = {
            "transaction_id": "TXN-12345",
            "status": "completed",
            "recipient_phone": "3001234567",
            "amount": 50000,
            "currency": "COP",
            "created_at": "2025-11-25T10:00:00Z",
            "message": "Transaction completed successfully"
        }

        result = get_transaction_status_tool.invoke({
            "transaction_id": "TXN-12345"
        })

        assert result["transaction_id"] == "TXN-12345"
        assert result["status"] == "completed"
        mock_client.get.assert_called_once_with("/api/v1/transactions/TXN-12345")

    @patch('apps.agents.transactional.tools.get_transaction_status.transaction_client')
    def test_get_pending_transaction_status(self, mock_client):
        """Test getting status of pending transaction."""
        mock_client.get.return_value = {
            "transaction_id": "TXN-12346",
            "status": "pending",
            "recipient_phone": "3001234567",
            "amount": 50000
        }

        result = get_transaction_status_tool.invoke({
            "transaction_id": "TXN-12346"
        })

        assert result["status"] == "pending"

    @patch('apps.agents.transactional.tools.get_transaction_status.transaction_client')
    def test_get_failed_transaction_status(self, mock_client):
        """Test getting status of failed transaction."""
        mock_client.get.return_value = {
            "transaction_id": "TXN-12347",
            "status": "failed",
            "recipient_phone": "3001234567",
            "amount": 50000,
            "message": "Insufficient funds"
        }

        result = get_transaction_status_tool.invoke({
            "transaction_id": "TXN-12347"
        })

        assert result["status"] == "failed"

    @patch('apps.agents.transactional.tools.get_transaction_status.transaction_client')
    def test_api_exception(self, mock_client):
        """Test handling of API exception."""
        mock_client.get.side_effect = Exception("Connection timeout")

        result = get_transaction_status_tool.invoke({
            "transaction_id": "TXN-12345"
        })

        assert "error" in result

    def test_empty_transaction_id(self):
        """Test with empty transaction ID."""
        result = get_transaction_status_tool.invoke({
            "transaction_id": ""
        })

        assert "error" in result
