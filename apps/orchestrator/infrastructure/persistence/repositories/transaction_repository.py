"""Transaction repository implementation.

Provides data access methods for Transaction entities following the
Repository pattern for clean separation of concerns.
"""

from datetime import datetime
from typing import Sequence
from uuid import UUID

from sqlalchemy import Select, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.orchestrator.domain.entities import Transaction, TransactionStatus
from apps.orchestrator.infrastructure.persistence.models import TransactionORM


class TransactionRepository:
    """Repository for Transaction aggregate.

    Handles all data access operations for transactions with proper
    conversion between domain entities and ORM models.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create(self, transaction: Transaction) -> Transaction:
        """Create a new transaction.

        Args:
            transaction: Transaction entity to persist

        Returns:
            Transaction: Created transaction with database-generated fields

        Example:
            ```python
            transaction = Transaction(
                user_id="user123",
                recipient_phone="3001234567",
                amount=50000.0,
            )
            saved = await repo.create(transaction)
            ```
        """
        orm_transaction = TransactionORM(
            id=transaction.id,
            conversation_id=transaction.id,  # Should be passed correctly
            external_transaction_id=transaction.external_transaction_id,
            user_id=transaction.user_id,
            recipient_phone=transaction.recipient_phone,
            amount=transaction.amount,
            currency=transaction.currency.value,
            status=transaction.status.value,
            validation_id=transaction.validation_id,
            error_message=transaction.error_message,
            created_at=transaction.created_at,
            completed_at=transaction.completed_at,
        )

        self.session.add(orm_transaction)
        await self.session.flush()
        await self.session.refresh(orm_transaction)

        return self._to_entity(orm_transaction)

    async def get_by_id(self, transaction_id: UUID) -> Transaction | None:
        """Get transaction by ID.

        Args:
            transaction_id: Transaction UUID

        Returns:
            Transaction entity or None if not found

        Example:
            ```python
            transaction = await repo.get_by_id(uuid4())
            if transaction:
                print(transaction.status)
            ```
        """
        stmt = select(TransactionORM).where(TransactionORM.id == transaction_id)
        result = await self.session.execute(stmt)
        orm_transaction = result.scalar_one_or_none()

        return self._to_entity(orm_transaction) if orm_transaction else None

    async def get_by_external_id(self, external_id: str) -> Transaction | None:
        """Get transaction by external transaction ID.

        Args:
            external_id: External transaction ID from payment service

        Returns:
            Transaction entity or None if not found

        Example:
            ```python
            transaction = await repo.get_by_external_id("txn_abc123")
            ```
        """
        stmt = select(TransactionORM).where(
            TransactionORM.external_transaction_id == external_id,
        )
        result = await self.session.execute(stmt)
        orm_transaction = result.scalar_one_or_none()

        return self._to_entity(orm_transaction) if orm_transaction else None

    async def get_by_user_id(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[Transaction]:
        """Get all transactions for a user.

        Args:
            user_id: User identifier
            limit: Maximum number of results (default 50)
            offset: Number of results to skip (default 0)

        Returns:
            List of Transaction entities ordered by creation date (newest first)

        Example:
            ```python
            transactions = await repo.get_by_user_id("user123", limit=10)
            for txn in transactions:
                print(txn.formatted_amount())
            ```
        """
        stmt = (
            select(TransactionORM)
            .where(TransactionORM.user_id == user_id)
            .order_by(desc(TransactionORM.created_at))
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        orm_transactions = result.scalars().all()

        return [self._to_entity(orm) for orm in orm_transactions]

    async def get_by_conversation_id(
        self,
        conversation_id: UUID,
    ) -> Sequence[Transaction]:
        """Get all transactions for a conversation.

        Args:
            conversation_id: Conversation UUID

        Returns:
            List of Transaction entities

        Example:
            ```python
            transactions = await repo.get_by_conversation_id(conv_id)
            ```
        """
        stmt = (
            select(TransactionORM)
            .where(TransactionORM.conversation_id == conversation_id)
            .order_by(TransactionORM.created_at)
        )
        result = await self.session.execute(stmt)
        orm_transactions = result.scalars().all()

        return [self._to_entity(orm) for orm in orm_transactions]

    async def update(self, transaction: Transaction) -> Transaction:
        """Update an existing transaction.

        Args:
            transaction: Transaction entity with updated values

        Returns:
            Updated transaction entity

        Raises:
            ValueError: If transaction not found

        Example:
            ```python
            transaction.mark_as_completed("ext_txn_123")
            updated = await repo.update(transaction)
            ```
        """
        stmt = select(TransactionORM).where(TransactionORM.id == transaction.id)
        result = await self.session.execute(stmt)
        orm_transaction = result.scalar_one_or_none()

        if not orm_transaction:
            msg = f"Transaction {transaction.id} not found"
            raise ValueError(msg)

        # Update fields
        orm_transaction.external_transaction_id = transaction.external_transaction_id
        orm_transaction.status = transaction.status.value
        orm_transaction.validation_id = transaction.validation_id
        orm_transaction.error_message = transaction.error_message
        orm_transaction.completed_at = transaction.completed_at
        orm_transaction.updated_at = datetime.utcnow()

        await self.session.flush()
        await self.session.refresh(orm_transaction)

        return self._to_entity(orm_transaction)

    async def update_status(
        self,
        transaction_id: UUID,
        status: TransactionStatus,
        error_message: str | None = None,
    ) -> Transaction:
        """Update transaction status.

        Args:
            transaction_id: Transaction UUID
            status: New status
            error_message: Optional error message for failed transactions

        Returns:
            Updated transaction entity

        Raises:
            ValueError: If transaction not found

        Example:
            ```python
            transaction = await repo.update_status(
                txn_id,
                TransactionStatus.FAILED,
                "Insufficient funds",
            )
            ```
        """
        stmt = select(TransactionORM).where(TransactionORM.id == transaction_id)
        result = await self.session.execute(stmt)
        orm_transaction = result.scalar_one_or_none()

        if not orm_transaction:
            msg = f"Transaction {transaction_id} not found"
            raise ValueError(msg)

        orm_transaction.status = status.value
        orm_transaction.error_message = error_message
        orm_transaction.updated_at = datetime.utcnow()

        if status in {
            TransactionStatus.COMPLETED,
            TransactionStatus.FAILED,
            TransactionStatus.CANCELLED,
        }:
            orm_transaction.completed_at = datetime.utcnow()

        await self.session.flush()
        await self.session.refresh(orm_transaction)

        return self._to_entity(orm_transaction)

    async def list_by_filters(
        self,
        status: TransactionStatus | None = None,
        user_id: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Transaction]:
        """List transactions with optional filters.

        Args:
            status: Filter by transaction status
            user_id: Filter by user ID
            start_date: Filter by created_at >= start_date
            end_date: Filter by created_at <= end_date
            limit: Maximum number of results (default 100)
            offset: Number of results to skip (default 0)

        Returns:
            List of Transaction entities matching filters

        Example:
            ```python
            # Get all pending transactions for a user
            transactions = await repo.list_by_filters(
                status=TransactionStatus.PENDING,
                user_id="user123",
                limit=50,
            )
            ```
        """
        stmt: Select = select(TransactionORM)

        # Apply filters
        if status:
            stmt = stmt.where(TransactionORM.status == status.value)
        if user_id:
            stmt = stmt.where(TransactionORM.user_id == user_id)
        if start_date:
            stmt = stmt.where(TransactionORM.created_at >= start_date)
        if end_date:
            stmt = stmt.where(TransactionORM.created_at <= end_date)

        # Order and paginate
        stmt = stmt.order_by(desc(TransactionORM.created_at)).limit(limit).offset(offset)

        result = await self.session.execute(stmt)
        orm_transactions = result.scalars().all()

        return [self._to_entity(orm) for orm in orm_transactions]

    async def count_by_status(self, user_id: str | None = None) -> dict[str, int]:
        """Count transactions by status.

        Args:
            user_id: Optional user ID to filter by

        Returns:
            Dictionary mapping status to count

        Example:
            ```python
            counts = await repo.count_by_status(user_id="user123")
            # {"pending": 2, "completed": 15, "failed": 1}
            ```
        """
        stmt = select(
            TransactionORM.status,
            func.count(TransactionORM.id).label("count"),
        ).group_by(TransactionORM.status)

        if user_id:
            stmt = stmt.where(TransactionORM.user_id == user_id)

        result = await self.session.execute(stmt)
        rows = result.all()

        return {row.status: row.count for row in rows}

    async def delete(self, transaction_id: UUID) -> bool:
        """Delete a transaction.

        Args:
            transaction_id: Transaction UUID

        Returns:
            True if deleted, False if not found

        Example:
            ```python
            deleted = await repo.delete(txn_id)
            ```
        """
        stmt = select(TransactionORM).where(TransactionORM.id == transaction_id)
        result = await self.session.execute(stmt)
        orm_transaction = result.scalar_one_or_none()

        if not orm_transaction:
            return False

        await self.session.delete(orm_transaction)
        await self.session.flush()

        return True

    def _to_entity(self, orm: TransactionORM) -> Transaction:
        """Convert ORM model to domain entity.

        Args:
            orm: TransactionORM instance

        Returns:
            Transaction domain entity
        """
        return Transaction(
            id=orm.id,
            external_transaction_id=orm.external_transaction_id,
            user_id=orm.user_id,
            recipient_phone=orm.recipient_phone,
            amount=orm.amount,
            currency=orm.currency,
            status=TransactionStatus(orm.status),
            validation_id=orm.validation_id,
            error_message=orm.error_message,
            created_at=orm.created_at,
            completed_at=orm.completed_at,
        )