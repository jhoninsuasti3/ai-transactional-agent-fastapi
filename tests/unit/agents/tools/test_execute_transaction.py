"""Tests for execute_transaction tool."""

import pytest
from unittest.mock import patch

from apps.agents.transactional.tools.execute_transaction import execute_transaction_tool


@pytest.mark.unit
class TestExecuteTransactionTool:
    """Test suite for execute_transaction_tool."""

    @patch('apps.agents.transactional.tools.execute_transaction.transaction_client')
    def test_successful_transaction_execution(self, mock_client):
        """Test successful transaction execution."""
        mock_client.post.return_value = {
            "transaction_id": "TXN-12345",
            "status": "completed",
            "message": "Transaction completed successfully"
        }

        result = execute_transaction_tool.invoke({
            "phone": "3001234567",
            "amount": 50000
        })

        assert result["success"] is True
        assert result["transaction_id"] == "TXN-12345"
        assert result["status"] == "completed"
        mock_client.post.assert_called_once()

    @patch('apps.agents.transactional.tools.execute_transaction.transaction_client')
    def test_failed_transaction_execution(self, mock_client):
        """Test failed transaction execution."""
        mock_client.post.return_value = {
            "transaction_id": "TXN-12346",
            "status": "failed",
            "message": "Insufficient funds"
        }

        result = execute_transaction_tool.invoke({
            "phone": "3001234567",
            "amount": 50000
        })

        assert result["success"] is False
        assert result["status"] == "failed"

    @patch('apps.agents.transactional.tools.execute_transaction.transaction_client')
    def test_pending_transaction(self, mock_client):
        """Test pending transaction status."""
        mock_client.post.return_value = {
            "transaction_id": "TXN-12347",
            "status": "pending",
            "message": "Transaction is being processed"
        }

        result = execute_transaction_tool.invoke({
            "phone": "3001234567",
            "amount": 50000
        })

        assert result["success"] is True  # pending is considered success
        assert result["status"] == "pending"

    @patch('apps.agents.transactional.tools.execute_transaction.transaction_client')
    def test_api_exception(self, mock_client):
        """Test handling of API exceptions."""
        mock_client.post.side_effect = Exception("Connection failed")

        result = execute_transaction_tool.invoke({
            "phone": "3001234567",
            "amount": 50000
        })

        assert result["success"] is False
        assert result["status"] == "failed"
        assert "error" in result

    def test_invalid_phone_number(self):
        """Test execution with invalid phone number."""
        result = execute_transaction_tool.invoke({
            "phone": "123",  # Invalid
            "amount": 50000
        })

        assert result["success"] is False
        assert result["status"] == "failed"
        assert "10 dígitos" in result["error"]

    def test_invalid_amount_pydantic(self):
        """Test execution with invalid amount (Pydantic validates)."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            execute_transaction_tool.invoke({
                "phone": "3001234567",
                "amount": -5000  # Negative amount
            })

    @patch('apps.agents.transactional.tools.execute_transaction.transaction_client')
    def test_large_transaction(self, mock_client):
        """Test execution of large transaction."""
        mock_client.post.return_value = {
            "transaction_id": "TXN-99999",
            "status": "completed",
            "message": "Large transaction completed"
        }

        result = execute_transaction_tool.invoke({
            "phone": "3001234567",
            "amount": 5000000  # 5 million
        })

        assert result["success"] is True
        assert result["transaction_id"] == "TXN-99999"

    @patch('apps.agents.transactional.tools.execute_transaction.transaction_client')
    def test_with_validation_id(self, mock_client):
        """Test execution with validation ID."""
        mock_client.post.return_value = {
            "transaction_id": "TXN-88888",
            "status": "completed",
            "message": "Transaction completed"
        }

        result = execute_transaction_tool.invoke({
            "phone": "3001234567",
            "amount": 50000,
            "validation_id": "VAL-12345"
        })

        assert result["success"] is True
        # Verify validation_id was included in the payload
        call_args = mock_client.post.call_args
        assert call_args[1]["json"]["validation_id"] == "VAL-12345"
