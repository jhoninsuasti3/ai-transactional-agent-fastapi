"""Unit tests for domain exceptions."""

from uuid import uuid4

import pytest

from apps.orchestrator.domain.exceptions.base import (
    BusinessRuleViolationError,
    DomainError,
    EntityAlreadyExistsError,
    EntityNotFoundError,
    InvalidStateTransitionError,
    ValidationError,
)


@pytest.mark.unit
class TestDomainError:
    """Test suite for DomainError base class."""

    def test_create_domain_exception_with_message_only(self):
        """Test creating domain exception with message only."""
        exc = DomainError("Something went wrong")
        assert exc.message == "Something went wrong"
        assert exc.details == {}
        assert str(exc) == "Something went wrong"

    def test_create_domain_exception_with_details(self):
        """Test creating domain exception with details."""
        details = {"code": "ERR_001", "severity": "high"}
        exc = DomainError("Error occurred", details=details)

        assert exc.message == "Error occurred"
        assert exc.details == details
        assert exc.details["code"] == "ERR_001"
        assert exc.details["severity"] == "high"

    def test_domain_exception_inherits_from_exception(self):
        """Test DomainError inherits from Exception."""
        exc = DomainError("Test error")
        assert isinstance(exc, Exception)

    def test_domain_exception_can_be_raised(self):
        """Test domain exception can be raised and caught."""
        with pytest.raises(DomainError) as exc_info:
            raise DomainError("Test error")

        assert exc_info.value.message == "Test error"

    def test_domain_exception_with_empty_details(self):
        """Test domain exception with None details becomes empty dict."""
        exc = DomainError("Error", details=None)
        assert exc.details == {}


@pytest.mark.unit
class TestEntityNotFoundError:
    """Test suite for EntityNotFoundError."""

    def test_create_entity_not_found_error(self):
        """Test creating entity not found error."""
        entity_id = uuid4()
        exc = EntityNotFoundError("Transaction", entity_id)

        assert "Transaction" in exc.message
        assert str(entity_id) in exc.message
        assert "not found" in exc.message
        assert exc.details["entity_name"] == "Transaction"
        assert exc.details["entity_id"] == entity_id

    def test_entity_not_found_with_string_id(self):
        """Test entity not found with string ID."""
        exc = EntityNotFoundError("User", "user-123")

        assert exc.message == "User with id 'user-123' not found"
        assert exc.details["entity_name"] == "User"
        assert exc.details["entity_id"] == "user-123"

    def test_entity_not_found_with_int_id(self):
        """Test entity not found with integer ID."""
        exc = EntityNotFoundError("Order", 12345)

        assert "Order" in exc.message
        assert "12345" in exc.message
        assert exc.details["entity_id"] == 12345

    def test_entity_not_found_inherits_from_domain_exception(self):
        """Test EntityNotFoundError inherits from DomainError."""
        exc = EntityNotFoundError("Test", 1)
        assert isinstance(exc, DomainError)
        assert isinstance(exc, Exception)

    def test_entity_not_found_can_be_raised(self):
        """Test entity not found error can be raised."""
        with pytest.raises(EntityNotFoundError) as exc_info:
            raise EntityNotFoundError("Product", "prod-999")

        assert "Product" in str(exc_info.value)
        assert "prod-999" in str(exc_info.value)


@pytest.mark.unit
class TestEntityAlreadyExistsError:
    """Test suite for EntityAlreadyExistsError."""

    def test_create_entity_already_exists_error(self):
        """Test creating entity already exists error."""
        exc = EntityAlreadyExistsError("User", "email", "test@example.com")

        assert "User" in exc.message
        assert "email" in exc.message
        assert "test@example.com" in exc.message
        assert "already exists" in exc.message
        assert exc.details["entity_name"] == "User"
        assert exc.details["unique_field"] == "email"
        assert exc.details["value"] == "test@example.com"

    def test_entity_already_exists_with_different_field(self):
        """Test entity already exists with different unique field."""
        exc = EntityAlreadyExistsError("Transaction", "transaction_id", "TXN-001")

        assert exc.message == "Transaction with transaction_id='TXN-001' already exists"
        assert exc.details["unique_field"] == "transaction_id"

    def test_entity_already_exists_with_numeric_value(self):
        """Test entity already exists with numeric value."""
        exc = EntityAlreadyExistsError("Account", "account_number", 123456)

        assert "123456" in exc.message
        assert exc.details["value"] == 123456

    def test_entity_already_exists_inherits_from_domain_exception(self):
        """Test EntityAlreadyExistsError inherits from DomainError."""
        exc = EntityAlreadyExistsError("Test", "field", "value")
        assert isinstance(exc, DomainError)

    def test_entity_already_exists_can_be_raised(self):
        """Test entity already exists error can be raised."""
        with pytest.raises(EntityAlreadyExistsError) as exc_info:
            raise EntityAlreadyExistsError("User", "username", "admin")

        assert "User" in str(exc_info.value)
        assert "username" in str(exc_info.value)


@pytest.mark.unit
class TestValidationError:
    """Test suite for ValidationError."""

    def test_create_validation_error_message_only(self):
        """Test creating validation error with message only."""
        exc = ValidationError("Invalid input")

        assert exc.message == "Invalid input"
        assert exc.details == {}

    def test_create_validation_error_with_field(self):
        """Test creating validation error with field."""
        exc = ValidationError("Phone number is invalid", field="phone")

        assert exc.message == "Phone number is invalid"
        assert exc.details["field"] == "phone"
        assert "value" not in exc.details

    def test_create_validation_error_with_field_and_value(self):
        """Test creating validation error with field and value."""
        exc = ValidationError("Amount must be positive", field="amount", value=-100)

        assert exc.message == "Amount must be positive"
        assert exc.details["field"] == "amount"
        assert exc.details["value"] == -100

    def test_validation_error_with_value_only(self):
        """Test validation error with value but no field."""
        exc = ValidationError("Invalid data", value="bad_value")

        assert exc.details["value"] == "bad_value"
        assert "field" not in exc.details

    def test_validation_error_with_zero_value(self):
        """Test validation error preserves zero value."""
        exc = ValidationError("Cannot be zero", field="count", value=0)

        # value=0 should be included in details (not treated as None)
        assert exc.details["value"] == 0
        assert exc.details["field"] == "count"

    def test_validation_error_inherits_from_domain_exception(self):
        """Test ValidationError inherits from DomainError."""
        exc = ValidationError("Test")
        assert isinstance(exc, DomainError)

    def test_validation_error_can_be_raised(self):
        """Test validation error can be raised."""
        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError("Invalid email", field="email", value="not-an-email")

        assert "Invalid email" in str(exc_info.value)
        assert exc_info.value.details["field"] == "email"


@pytest.mark.unit
class TestBusinessRuleViolationError:
    """Test suite for BusinessRuleViolationError."""

    def test_create_business_rule_violation_without_context(self):
        """Test creating business rule violation without context."""
        exc = BusinessRuleViolationError(
            "MAX_DAILY_TRANSACTIONS", "User has exceeded maximum daily transactions"
        )

        assert exc.message == "User has exceeded maximum daily transactions"
        assert exc.details["rule"] == "MAX_DAILY_TRANSACTIONS"
        assert len(exc.details) == 1  # Only rule, no context

    def test_create_business_rule_violation_with_context(self):
        """Test creating business rule violation with context."""
        context = {"user_id": "user-123", "current_count": 10, "max_allowed": 5}
        exc = BusinessRuleViolationError(
            "MAX_DAILY_TRANSACTIONS", "Too many transactions", context=context
        )

        assert exc.message == "Too many transactions"
        assert exc.details["rule"] == "MAX_DAILY_TRANSACTIONS"
        assert exc.details["user_id"] == "user-123"
        assert exc.details["current_count"] == 10
        assert exc.details["max_allowed"] == 5

    def test_business_rule_violation_context_merged_with_rule(self):
        """Test context is merged with rule in details."""
        context = {"amount": 10000, "limit": 5000}
        exc = BusinessRuleViolationError("AMOUNT_LIMIT", "Amount exceeds limit", context)

        # Both rule and context should be in details
        assert "rule" in exc.details
        assert "amount" in exc.details
        assert "limit" in exc.details

    def test_business_rule_violation_with_none_context(self):
        """Test business rule violation with None context."""
        exc = BusinessRuleViolationError("TEST_RULE", "Test message", context=None)

        assert exc.details["rule"] == "TEST_RULE"
        assert len(exc.details) == 1

    def test_business_rule_violation_inherits_from_domain_exception(self):
        """Test BusinessRuleViolationError inherits from DomainError."""
        exc = BusinessRuleViolationError("RULE", "Message")
        assert isinstance(exc, DomainError)

    def test_business_rule_violation_can_be_raised(self):
        """Test business rule violation can be raised."""
        with pytest.raises(BusinessRuleViolationError) as exc_info:
            raise BusinessRuleViolationError(
                "INSUFFICIENT_FUNDS", "Account balance too low", {"balance": 100, "required": 500}
            )

        assert "Account balance too low" in str(exc_info.value)
        assert exc_info.value.details["rule"] == "INSUFFICIENT_FUNDS"


@pytest.mark.unit
class TestInvalidStateTransitionError:
    """Test suite for InvalidStateTransitionError."""

    def test_create_invalid_state_transition(self):
        """Test creating invalid state transition error."""
        exc = InvalidStateTransitionError("Transaction", "completed", "pending")

        assert "Invalid transition" in exc.message
        assert "Transaction" in exc.message
        assert "completed" in exc.message
        assert "pending" in exc.message
        assert exc.details["entity"] == "Transaction"
        assert exc.details["from_state"] == "completed"
        assert exc.details["to_state"] == "pending"

    def test_invalid_state_transition_message_format(self):
        """Test message format of invalid state transition."""
        exc = InvalidStateTransitionError("Order", "shipped", "pending")

        expected = "Invalid transition for Order: shipped -> pending"
        assert exc.message == expected

    def test_invalid_state_transition_with_different_states(self):
        """Test invalid state transition with different states."""
        exc = InvalidStateTransitionError("Conversation", "abandoned", "active")

        assert exc.details["entity"] == "Conversation"
        assert exc.details["from_state"] == "abandoned"
        assert exc.details["to_state"] == "active"

    def test_invalid_state_transition_inherits_from_domain_exception(self):
        """Test InvalidStateTransitionError inherits from DomainError."""
        exc = InvalidStateTransitionError("Test", "state1", "state2")
        assert isinstance(exc, DomainError)

    def test_invalid_state_transition_can_be_raised(self):
        """Test invalid state transition can be raised."""
        with pytest.raises(InvalidStateTransitionError) as exc_info:
            raise InvalidStateTransitionError("Payment", "refunded", "processing")

        assert "Payment" in str(exc_info.value)
        assert "refunded" in str(exc_info.value)
        assert "processing" in str(exc_info.value)


@pytest.mark.unit
class TestExceptionHierarchy:
    """Test suite for exception hierarchy."""

    def test_all_custom_exceptions_inherit_from_domain_exception(self):
        """Test all custom exceptions inherit from DomainError."""
        exceptions = [
            EntityNotFoundError("Test", 1),
            EntityAlreadyExistsError("Test", "field", "value"),
            ValidationError("Test"),
            BusinessRuleViolationError("RULE", "Message"),
            InvalidStateTransitionError("Entity", "from", "to"),
        ]

        for exc in exceptions:
            assert isinstance(exc, DomainError)
            assert isinstance(exc, Exception)

    def test_can_catch_all_domain_exceptions(self):
        """Test can catch all domain exceptions with DomainError."""
        # EntityNotFoundError
        with pytest.raises(DomainError):
            raise EntityNotFoundError("Test", 1)

        # EntityAlreadyExistsError
        with pytest.raises(DomainError):
            raise EntityAlreadyExistsError("Test", "field", "value")

        # ValidationError
        with pytest.raises(DomainError):
            raise ValidationError("Test")

        # BusinessRuleViolationError
        with pytest.raises(DomainError):
            raise BusinessRuleViolationError("RULE", "Message")

        # InvalidStateTransitionError
        with pytest.raises(DomainError):
            raise InvalidStateTransitionError("Entity", "from", "to")

    def test_can_catch_specific_exceptions(self):
        """Test can catch specific exception types."""
        with pytest.raises(EntityNotFoundError):
            raise EntityNotFoundError("Test", 1)

        with pytest.raises(ValidationError):
            raise ValidationError("Test")
