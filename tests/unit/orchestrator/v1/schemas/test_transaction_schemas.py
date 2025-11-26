"""Unit tests for transaction schemas."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from apps.orchestrator.v1.schemas.transaction import (
    TransactionStatus,
    TransactionCreate,
    TransactionResponse,
    TransactionDetail,
)


@pytest.mark.unit
class TestTransactionStatus:
    """Test suite for TransactionStatus enum."""

    def test_transaction_status_values(self):
        """Test transaction status enum values."""
        assert TransactionStatus.PENDING == "pending"
        assert TransactionStatus.COMPLETED == "completed"
        assert TransactionStatus.FAILED == "failed"


@pytest.mark.unit
class TestTransactionCreate:
    """Test suite for TransactionCreate schema."""

    def test_valid_transaction_create(self):
        """Test valid transaction creation."""
        transaction = TransactionCreate(
            recipient_phone="3001234567",
            amount=50000
        )
        assert transaction.recipient_phone == "3001234567"
        assert transaction.amount == 50000
        assert transaction.currency == "COP"

    def test_transaction_with_custom_currency(self):
        """Test transaction with custom currency."""
        transaction = TransactionCreate(
            recipient_phone="3001234567",
            amount=100.50,
            currency="USD"
        )
        assert transaction.currency == "USD"

    def test_invalid_phone_pattern_fails(self):
        """Test that invalid phone pattern fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            TransactionCreate(
                recipient_phone="123",
                amount=50000
            )
        assert "recipient_phone" in str(exc_info.value)

    def test_phone_with_non_digits_fails(self):
        """Test that phone with non-digits fails validation."""
        with pytest.raises(ValidationError):
            TransactionCreate(
                recipient_phone="300ABC4567",
                amount=50000
            )

    def test_negative_amount_fails(self):
        """Test that negative amount fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            TransactionCreate(
                recipient_phone="3001234567",
                amount=-1000
            )
        assert "amount" in str(exc_info.value)

    def test_zero_amount_fails(self):
        """Test that zero amount fails validation."""
        with pytest.raises(ValidationError):
            TransactionCreate(
                recipient_phone="3001234567",
                amount=0
            )

    def test_missing_required_fields_fail(self):
        """Test that missing required fields fail validation."""
        with pytest.raises(ValidationError):
            TransactionCreate(recipient_phone="3001234567")


@pytest.mark.unit
class TestTransactionResponse:
    """Test suite for TransactionResponse schema."""

    def test_valid_transaction_response(self):
        """Test valid transaction response creation."""
        now = datetime.utcnow()
        response = TransactionResponse(
            transaction_id="TXN-12345",
            status=TransactionStatus.COMPLETED,
            recipient_phone="3001234567",
            amount=50000,
            currency="COP",
            created_at=now
        )
        assert response.transaction_id == "TXN-12345"
        assert response.status == TransactionStatus.COMPLETED
        assert response.recipient_phone == "3001234567"
        assert response.amount == 50000
        assert response.completed_at is None
        assert response.error_message is None

    def test_transaction_response_with_completion(self):
        """Test transaction response with completion timestamp."""
        created = datetime.utcnow()
        completed = datetime.utcnow()
        response = TransactionResponse(
            transaction_id="TXN-12345",
            status=TransactionStatus.COMPLETED,
            recipient_phone="3001234567",
            amount=50000,
            currency="COP",
            created_at=created,
            completed_at=completed
        )
        assert response.completed_at == completed

    def test_transaction_response_failed_with_error(self):
        """Test failed transaction response with error message."""
        response = TransactionResponse(
            transaction_id="TXN-12345",
            status=TransactionStatus.FAILED,
            recipient_phone="3001234567",
            amount=50000,
            currency="COP",
            created_at=datetime.utcnow(),
            error_message="Insufficient funds"
        )
        assert response.status == TransactionStatus.FAILED
        assert response.error_message == "Insufficient funds"


@pytest.mark.unit
class TestTransactionDetail:
    """Test suite for TransactionDetail schema."""

    def test_valid_transaction_detail(self):
        """Test valid transaction detail creation."""
        detail = TransactionDetail(
            transaction_id="TXN-12345",
            conversation_id="conv-123",
            status=TransactionStatus.COMPLETED,
            recipient_phone="3001234567",
            amount=50000,
            currency="COP",
            created_at=datetime.utcnow()
        )
        assert detail.transaction_id == "TXN-12345"
        assert detail.conversation_id == "conv-123"
        assert detail.metadata is None

    def test_transaction_detail_with_metadata(self):
        """Test transaction detail with metadata."""
        metadata = {
            "user_id": "user-123",
            "device": "mobile",
            "ip_address": "192.168.1.1"
        }
        detail = TransactionDetail(
            transaction_id="TXN-12345",
            conversation_id="conv-123",
            status=TransactionStatus.PENDING,
            recipient_phone="3001234567",
            amount=50000,
            currency="COP",
            created_at=datetime.utcnow(),
            metadata=metadata
        )
        assert detail.metadata == metadata
        assert detail.metadata["user_id"] == "user-123"
