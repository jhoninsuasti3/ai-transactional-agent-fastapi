"""Tests for validate_transaction tool."""

import pytest
from unittest.mock import patch, MagicMock

from apps.agents.transactional.tools.validate_transaction import validate_transaction_tool


@pytest.mark.unit
class TestValidateTransactionTool:
    """Test suite for validate_transaction_tool."""

    def test_invalid_phone_format_too_short(self):
        """Test validation with phone too short."""
        result = validate_transaction_tool.invoke({
            "phone": "123",  # Too short
            "amount": 50000
        })

        assert result["valid"] is False
        assert "10 dígitos" in result["error"]

    def test_invalid_phone_format_too_long(self):
        """Test validation with phone too long."""
        result = validate_transaction_tool.invoke({
            "phone": "12345678901",  # Too long
            "amount": 50000
        })

        assert result["valid"] is False
        assert "10 dígitos" in result["error"]

    def test_invalid_amount_checked_by_pydantic(self):
        """Test that Pydantic validates amount > 0."""
        # Pydantic validation happens before the function runs
        # So we expect a ValidationError for amounts <= 0
        with pytest.raises(Exception):  # Pydantic ValidationError
            validate_transaction_tool.invoke({
                "phone": "3001234567",
                "amount": -1000
            })

    def test_invalid_amount_zero_checked_by_pydantic(self):
        """Test that Pydantic validates amount > 0."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            validate_transaction_tool.invoke({
                "phone": "3001234567",
                "amount": 0
            })

    @patch('apps.agents.transactional.tools.validate_transaction.transaction_client')
    def test_valid_transaction_success(self, mock_client):
        """Test successful transaction validation."""
        mock_client.post.return_value = {
            "is_valid": True,
            "message": "Transaction can be processed",
            "validation_id": "VAL-12345"
        }

        result = validate_transaction_tool.invoke({
            "phone": "3001234567",
            "amount": 50000
        })

        assert result["valid"] is True
        assert "validation_id" in result
        mock_client.post.assert_called_once()

    @patch('apps.agents.transactional.tools.validate_transaction.transaction_client')
    def test_api_returns_invalid(self, mock_client):
        """Test when API returns transaction is invalid."""
        mock_client.post.return_value = {
            "is_valid": False,
            "message": "Insufficient funds"
        }

        result = validate_transaction_tool.invoke({
            "phone": "3001234567",
            "amount": 50000
        })

        assert result["valid"] is False

    @patch('apps.agents.transactional.tools.validate_transaction.transaction_client')
    def test_api_error_exception(self, mock_client):
        """Test handling of API exceptions."""
        mock_client.post.side_effect = Exception("Connection timeout")

        result = validate_transaction_tool.invoke({
            "phone": "3001234567",
            "amount": 50000
        })

        assert result["valid"] is False
        assert "error" in result

    @patch('apps.agents.transactional.tools.validate_transaction.transaction_client')
    def test_large_amount(self, mock_client):
        """Test validation with large amount."""
        mock_client.post.return_value = {
            "is_valid": True,
            "message": "Transaction can be processed",
            "validation_id": "VAL-99999"
        }

        result = validate_transaction_tool.invoke({
            "phone": "3001234567",
            "amount": 10000000  # 10 million
        })

        assert result["valid"] is True

    @patch('apps.agents.transactional.tools.validate_transaction.transaction_client')
    def test_small_amount(self, mock_client):
        """Test validation with small amount."""
        mock_client.post.return_value = {
            "is_valid": True,
            "message": "Transaction can be processed",
            "validation_id": "VAL-11111"
        }

        result = validate_transaction_tool.invoke({
            "phone": "3001234567",
            "amount": 1000  # Small amount
        })

        assert result["valid"] is True
