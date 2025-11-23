"""Transaction service port - Interface for external transaction services."""

from abc import ABC, abstractmethod

from src.apps.domain.models import TransactionValidation, TransactionExecution


class TransactionPort(ABC):
    """Port (interface) for external transaction service.

    This defines the contract that must be implemented by infrastructure adapters
    (like TransactionClient) to communicate with payment processing services.
    """

    @abstractmethod
    async def validate_transaction(
        self,
        recipient_phone: str,
        amount: float,
    ) -> TransactionValidation:
        """Validate a transaction before execution.

        Args:
            recipient_phone: Recipient's phone number
            amount: Transaction amount

        Returns:
            TransactionValidation with result

        Raises:
            TransactionValidationError: Validation failed
            ExternalServiceError: Service unavailable
        """
        pass

    @abstractmethod
    async def execute_transaction(
        self,
        recipient_phone: str,
        amount: float,
    ) -> TransactionExecution:
        """Execute a validated transaction.

        Args:
            recipient_phone: Recipient's phone number
            amount: Transaction amount

        Returns:
            TransactionExecution with transaction details

        Raises:
            ExternalServiceError: Service unavailable or execution failed
        """
        pass

    @abstractmethod
    async def get_transaction_status(
        self,
        transaction_id: str,
    ) -> TransactionExecution:
        """Get current status of a transaction.

        Args:
            transaction_id: Unique transaction identifier

        Returns:
            TransactionExecution with current status

        Raises:
            ExternalServiceError: Service unavailable or not found
        """
        pass