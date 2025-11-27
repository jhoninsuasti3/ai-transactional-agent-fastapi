"""Unit tests for core exceptions."""

import pytest

from apps.orchestrator.core.exceptions import (
    AppError,
    ApplicationError,
    BusinessRuleViolationError,
    DatabaseError,
    DomainError,
    ExternalServiceError,
    InfrastructureError,
    NotFoundError,
    TransactionValidationError,
    ValidationError,
)


@pytest.mark.unit
class TestAppError:
    """Test suite for base AppError."""

    def test_app_exception_with_message_only(self):
        """Test AppError with message only."""
        exc = AppError("Something went wrong")
        assert str(exc) == "Something went wrong"
        assert exc.message == "Something went wrong"
        assert exc.details == {}

    def test_app_exception_with_details(self):
        """Test AppError with details."""
        details = {"code": "ERR001", "field": "email"}
        exc = AppError("Invalid email", details=details)

        assert exc.message == "Invalid email"
        assert exc.details == details
        assert exc.details["code"] == "ERR001"
        assert exc.details["field"] == "email"

    def test_app_exception_is_exception(self):
        """Test AppError is an Exception."""
        exc = AppError("Test")
        assert isinstance(exc, Exception)


@pytest.mark.unit
class TestDomainErrors:
    """Test suite for domain exceptions."""

    def test_domain_exception(self):
        """Test DomainError."""
        exc = DomainError("Domain error")
        assert isinstance(exc, AppError)
        assert exc.message == "Domain error"

    def test_validation_error(self):
        """Test ValidationError."""
        exc = ValidationError("Invalid phone number", details={"field": "phone"})
        assert isinstance(exc, DomainError)
        assert exc.message == "Invalid phone number"
        assert exc.details["field"] == "phone"

    def test_business_rule_violation(self):
        """Test BusinessRuleViolationError."""
        exc = BusinessRuleViolationError(
            "Cannot send more than daily limit", details={"limit": 1000000, "attempted": 2000000}
        )
        assert isinstance(exc, DomainError)
        assert exc.message == "Cannot send more than daily limit"
        assert exc.details["limit"] == 1000000


@pytest.mark.unit
class TestInfrastructureErrors:
    """Test suite for infrastructure exceptions."""

    def test_infrastructure_exception(self):
        """Test InfrastructureError."""
        exc = InfrastructureError("Infrastructure error")
        assert isinstance(exc, AppError)
        assert exc.message == "Infrastructure error"

    def test_external_service_error(self):
        """Test ExternalServiceError."""
        exc = ExternalServiceError(
            "Payment service unavailable", details={"service": "payment", "status_code": 503}
        )
        assert isinstance(exc, InfrastructureError)
        assert exc.message == "Payment service unavailable"
        assert exc.details["service"] == "payment"
        assert exc.details["status_code"] == 503

    def test_transaction_validation_error(self):
        """Test TransactionValidationError."""
        exc = TransactionValidationError(
            "Insufficient funds", details={"balance": 10000, "amount": 50000}
        )
        assert isinstance(exc, InfrastructureError)
        assert exc.message == "Insufficient funds"

    def test_database_error(self):
        """Test DatabaseError."""
        exc = DatabaseError(
            "Connection timeout", details={"operation": "insert", "table": "transactions"}
        )
        assert isinstance(exc, InfrastructureError)
        assert exc.message == "Connection timeout"


@pytest.mark.unit
class TestApplicationErrors:
    """Test suite for application exceptions."""

    def test_application_exception(self):
        """Test ApplicationError."""
        exc = ApplicationError("Application error")
        assert isinstance(exc, AppError)
        assert exc.message == "Application error"

    def test_not_found_error(self):
        """Test NotFoundError."""
        exc = NotFoundError("Transaction", "TXN-12345")
        assert isinstance(exc, ApplicationError)
        assert "Transaction" in exc.message
        assert "TXN-12345" in exc.message
        assert exc.details["resource"] == "Transaction"
        assert exc.details["identifier"] == "TXN-12345"


@pytest.mark.unit
class TestExceptionHierarchy:
    """Test exception hierarchy relationships."""

    def test_domain_exception_hierarchy(self):
        """Test domain exception hierarchy."""
        assert issubclass(DomainError, AppError)
        assert issubclass(ValidationError, DomainError)
        assert issubclass(BusinessRuleViolationError, DomainError)

    def test_infrastructure_exception_hierarchy(self):
        """Test infrastructure exception hierarchy."""
        assert issubclass(InfrastructureError, AppError)
        assert issubclass(ExternalServiceError, InfrastructureError)
        assert issubclass(TransactionValidationError, InfrastructureError)
        assert issubclass(DatabaseError, InfrastructureError)

    def test_application_exception_hierarchy(self):
        """Test application exception hierarchy."""
        assert issubclass(ApplicationError, AppError)
        assert issubclass(NotFoundError, ApplicationError)

    def test_all_exceptions_are_exception(self):
        """Test all custom exceptions are Exception."""
        exceptions = [
            AppError,
            DomainError,
            ValidationError,
            BusinessRuleViolationError,
            InfrastructureError,
            ExternalServiceError,
            TransactionValidationError,
            DatabaseError,
            ApplicationError,
            NotFoundError,
        ]

        for exc_class in exceptions:
            assert issubclass(exc_class, Exception)
