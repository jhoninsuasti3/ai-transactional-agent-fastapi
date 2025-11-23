"""Repository ports - Interfaces for data persistence."""

from abc import ABC, abstractmethod
from typing import Any

from apps.apps.domain.models import Conversation, Transaction, ConversationStatus


class ConversationRepository(ABC):
    """Port (interface) for conversation persistence."""

    @abstractmethod
    async def create(self, conversation: Conversation) -> Conversation:
        """Create a new conversation.

        Args:
            conversation: Conversation entity to create

        Returns:
            Created conversation with assigned ID
        """
        pass

    @abstractmethod
    async def get_by_id(self, conversation_id: int) -> Conversation | None:
        """Get conversation by ID.

        Args:
            conversation_id: Conversation ID

        Returns:
            Conversation if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> list[Conversation]:
        """Get all conversations for a user.

        Args:
            user_id: User identifier

        Returns:
            List of conversations (may be empty)
        """
        pass

    @abstractmethod
    async def update_status(
        self,
        conversation_id: int,
        status: ConversationStatus,
    ) -> Conversation:
        """Update conversation status.

        Args:
            conversation_id: Conversation ID
            status: New status

        Returns:
            Updated conversation

        Raises:
            NotFoundError: Conversation not found
        """
        pass

    @abstractmethod
    async def update_agent_state(
        self,
        conversation_id: int,
        agent_state: dict[str, Any],
    ) -> Conversation:
        """Update LangGraph agent state.

        Args:
            conversation_id: Conversation ID
            agent_state: New agent state snapshot

        Returns:
            Updated conversation

        Raises:
            NotFoundError: Conversation not found
        """
        pass

    @abstractmethod
    async def delete(self, conversation_id: int) -> None:
        """Delete a conversation.

        Args:
            conversation_id: Conversation ID

        Raises:
            NotFoundError: Conversation not found
        """
        pass


class TransactionRepository(ABC):
    """Port (interface) for transaction persistence."""

    @abstractmethod
    async def create(self, transaction: Transaction) -> Transaction:
        """Create a new transaction.

        Args:
            transaction: Transaction entity to create

        Returns:
            Created transaction with assigned ID
        """
        pass

    @abstractmethod
    async def get_by_id(self, transaction_id: int) -> Transaction | None:
        """Get transaction by database ID.

        Args:
            transaction_id: Database transaction ID

        Returns:
            Transaction if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_external_id(
        self,
        external_transaction_id: str,
    ) -> Transaction | None:
        """Get transaction by external service ID.

        Args:
            external_transaction_id: Transaction ID from external service

        Returns:
            Transaction if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_conversation_id(
        self,
        conversation_id: int,
    ) -> list[Transaction]:
        """Get all transactions for a conversation.

        Args:
            conversation_id: Conversation ID

        Returns:
            List of transactions (may be empty)
        """
        pass

    @abstractmethod
    async def update_status(
        self,
        transaction_id: int,
        status: str,
        error_message: str | None = None,
    ) -> Transaction:
        """Update transaction status.

        Args:
            transaction_id: Database transaction ID
            status: New status
            error_message: Error message if failed

        Returns:
            Updated transaction

        Raises:
            NotFoundError: Transaction not found
        """
        pass

    @abstractmethod
    async def delete(self, transaction_id: int) -> None:
        """Delete a transaction.

        Args:
            transaction_id: Database transaction ID

        Raises:
            NotFoundError: Transaction not found
        """
        pass