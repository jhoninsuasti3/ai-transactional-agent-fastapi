"""Unit tests for core exceptions."""

import pytest

from apps.orchestrator.core.exceptions import (
    AppException,
    ApplicationException,
    BusinessRuleViolation,
    DatabaseError,
    DomainException,
    ExternalServiceError,
    InfrastructureException,
    NotFoundError,
    TransactionValidationError,
    ValidationError,
)


@pytest.mark.unit
class TestAppException:
    """Test suite for base AppException."""

    def test_app_exception_with_message_only(self):
        """Test AppException with message only."""
        exc = AppException("Something went wrong")
        assert str(exc) == "Something went wrong"
        assert exc.message == "Something went wrong"
        assert exc.details == {}

    def test_app_exception_with_details(self):
        """Test AppException with details."""
        details = {"code": "ERR001", "field": "email"}
        exc = AppException("Invalid email", details=details)

        assert exc.message == "Invalid email"
        assert exc.details == details
        assert exc.details["code"] == "ERR001"
        assert exc.details["field"] == "email"

    def test_app_exception_is_exception(self):
        """Test AppException is an Exception."""
        exc = AppException("Test")
        assert isinstance(exc, Exception)


@pytest.mark.unit
class TestDomainExceptions:
    """Test suite for domain exceptions."""

    def test_domain_exception(self):
        """Test DomainException."""
        exc = DomainException("Domain error")
        assert isinstance(exc, AppException)
        assert exc.message == "Domain error"

    def test_validation_error(self):
        """Test ValidationError."""
        exc = ValidationError("Invalid phone number", details={"field": "phone"})
        assert isinstance(exc, DomainException)
        assert exc.message == "Invalid phone number"
        assert exc.details["field"] == "phone"

    def test_business_rule_violation(self):
        """Test BusinessRuleViolation."""
        exc = BusinessRuleViolation(
            "Cannot send more than daily limit", details={"limit": 1000000, "attempted": 2000000}
        )
        assert isinstance(exc, DomainException)
        assert exc.message == "Cannot send more than daily limit"
        assert exc.details["limit"] == 1000000


@pytest.mark.unit
class TestInfrastructureExceptions:
    """Test suite for infrastructure exceptions."""

    def test_infrastructure_exception(self):
        """Test InfrastructureException."""
        exc = InfrastructureException("Infrastructure error")
        assert isinstance(exc, AppException)
        assert exc.message == "Infrastructure error"

    def test_external_service_error(self):
        """Test ExternalServiceError."""
        exc = ExternalServiceError(
            "Payment service unavailable", details={"service": "payment", "status_code": 503}
        )
        assert isinstance(exc, InfrastructureException)
        assert exc.message == "Payment service unavailable"
        assert exc.details["service"] == "payment"
        assert exc.details["status_code"] == 503

    def test_transaction_validation_error(self):
        """Test TransactionValidationError."""
        exc = TransactionValidationError(
            "Insufficient funds", details={"balance": 10000, "amount": 50000}
        )
        assert isinstance(exc, InfrastructureException)
        assert exc.message == "Insufficient funds"

    def test_database_error(self):
        """Test DatabaseError."""
        exc = DatabaseError(
            "Connection timeout", details={"operation": "insert", "table": "transactions"}
        )
        assert isinstance(exc, InfrastructureException)
        assert exc.message == "Connection timeout"


@pytest.mark.unit
class TestApplicationExceptions:
    """Test suite for application exceptions."""

    def test_application_exception(self):
        """Test ApplicationException."""
        exc = ApplicationException("Application error")
        assert isinstance(exc, AppException)
        assert exc.message == "Application error"

    def test_not_found_error(self):
        """Test NotFoundError."""
        exc = NotFoundError("Transaction", "TXN-12345")
        assert isinstance(exc, ApplicationException)
        assert "Transaction" in exc.message
        assert "TXN-12345" in exc.message
        assert exc.details["resource"] == "Transaction"
        assert exc.details["identifier"] == "TXN-12345"


@pytest.mark.unit
class TestExceptionHierarchy:
    """Test exception hierarchy relationships."""

    def test_domain_exception_hierarchy(self):
        """Test domain exception hierarchy."""
        assert issubclass(DomainException, AppException)
        assert issubclass(ValidationError, DomainException)
        assert issubclass(BusinessRuleViolation, DomainException)

    def test_infrastructure_exception_hierarchy(self):
        """Test infrastructure exception hierarchy."""
        assert issubclass(InfrastructureException, AppException)
        assert issubclass(ExternalServiceError, InfrastructureException)
        assert issubclass(TransactionValidationError, InfrastructureException)
        assert issubclass(DatabaseError, InfrastructureException)

    def test_application_exception_hierarchy(self):
        """Test application exception hierarchy."""
        assert issubclass(ApplicationException, AppException)
        assert issubclass(NotFoundError, ApplicationException)

    def test_all_exceptions_are_exception(self):
        """Test all custom exceptions are Exception."""
        exceptions = [
            AppException,
            DomainException,
            ValidationError,
            BusinessRuleViolation,
            InfrastructureException,
            ExternalServiceError,
            TransactionValidationError,
            DatabaseError,
            ApplicationException,
            NotFoundError,
        ]

        for exc_class in exceptions:
            assert issubclass(exc_class, Exception)
