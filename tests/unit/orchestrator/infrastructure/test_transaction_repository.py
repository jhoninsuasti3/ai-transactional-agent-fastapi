"""Unit tests for TransactionRepository."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, Mock
from uuid import uuid4

from apps.orchestrator.domain.entities import Transaction, TransactionStatus, Currency
from apps.orchestrator.infrastructure.persistence.repositories.transaction_repository import (
    TransactionRepository,
)
from apps.orchestrator.infrastructure.persistence.models import TransactionORM


@pytest.mark.unit
class TestTransactionRepository:
    """Test suite for TransactionRepository."""

    @pytest.fixture
    def mock_session(self):
        """Create mock AsyncSession."""
        session = AsyncMock()
        session.add = Mock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        session.delete = AsyncMock()
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def sample_transaction(self):
        """Create sample Transaction entity."""
        txn = Transaction(
            user_id="user-123",
            recipient_phone="3001234567",
            amount=50000.0,
            currency=Currency.COP
        )
        # Manually set currency and status as enum objects (not strings)
        # since use_enum_values might convert them
        object.__setattr__(txn, 'currency', Currency.COP)
        object.__setattr__(txn, 'status', TransactionStatus.PENDING)
        return txn

    @pytest.fixture
    def sample_orm(self, sample_transaction):
        """Create sample TransactionORM."""
        return TransactionORM(
            id=sample_transaction.id,
            conversation_id=sample_transaction.id,
            external_transaction_id=None,
            user_id=sample_transaction.user_id,
            recipient_phone=sample_transaction.recipient_phone,
            amount=sample_transaction.amount,
            currency="COP",
            status="pending",
            validation_id=None,
            error_message=None,
            created_at=sample_transaction.created_at,
            completed_at=None,
        )

    @pytest.mark.asyncio
    async def test_repository_initialization(self, mock_session):
        """Test repository initializes with session."""
        repo = TransactionRepository(mock_session)
        assert repo.session == mock_session

    @pytest.mark.asyncio
    async def test_create_transaction(self, mock_session, sample_transaction, sample_orm):
        """Test creating a new transaction."""
        repo = TransactionRepository(mock_session)

        # Mock refresh to set orm attributes
        async def refresh_side_effect(orm):
            # ORM already has attributes set
            pass

        mock_session.refresh.side_effect = refresh_side_effect

        result = await repo.create(sample_transaction)

        # Verify session operations
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()

        # Verify result is a Transaction entity
        assert isinstance(result, Transaction)
        assert result.user_id == "user-123"
        assert result.recipient_phone == "3001234567"
        assert result.amount == 50000.0

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, mock_session, sample_orm):
        """Test getting transaction by ID when found."""
        repo = TransactionRepository(mock_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_orm
        mock_session.execute.return_value = mock_result

        transaction = await repo.get_by_id(sample_orm.id)

        assert transaction is not None
        assert transaction.id == sample_orm.id
        assert transaction.user_id == sample_orm.user_id
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, mock_session):
        """Test getting transaction by ID when not found."""
        repo = TransactionRepository(mock_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        transaction = await repo.get_by_id(uuid4())

        assert transaction is None
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_external_id_found(self, mock_session, sample_orm):
        """Test getting transaction by external ID."""
        sample_orm.external_transaction_id = "EXT-123"
        repo = TransactionRepository(mock_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_orm
        mock_session.execute.return_value = mock_result

        transaction = await repo.get_by_external_id("EXT-123")

        assert transaction is not None
        assert transaction.external_transaction_id == "EXT-123"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_external_id_not_found(self, mock_session):
        """Test getting transaction by external ID when not found."""
        repo = TransactionRepository(mock_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        transaction = await repo.get_by_external_id("NOT-EXIST")

        assert transaction is None

    @pytest.mark.asyncio
    async def test_get_by_user_id(self, mock_session, sample_orm):
        """Test getting transactions by user ID."""
        repo = TransactionRepository(mock_session)

        orm_list = [sample_orm]
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = orm_list
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        transactions = await repo.get_by_user_id("user-123", limit=10, offset=0)

        assert len(transactions) == 1
        assert transactions[0].user_id == "user-123"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_conversation_id(self, mock_session, sample_orm):
        """Test getting transactions by conversation ID."""
        repo = TransactionRepository(mock_session)
        conv_id = uuid4()
        sample_orm.conversation_id = conv_id

        orm_list = [sample_orm]
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = orm_list
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        transactions = await repo.get_by_conversation_id(conv_id)

        assert len(transactions) == 1
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_transaction(self, mock_session, sample_transaction, sample_orm):
        """Test updating an existing transaction."""
        repo = TransactionRepository(mock_session)

        sample_transaction.external_transaction_id = "EXT-999"
        sample_transaction.mark_as_completed("EXT-999")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_orm
        mock_session.execute.return_value = mock_result

        updated = await repo.update(sample_transaction)

        assert isinstance(updated, Transaction)
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_transaction_not_found(self, mock_session, sample_transaction):
        """Test updating transaction that doesn't exist."""
        repo = TransactionRepository(mock_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        with pytest.raises(ValueError) as exc_info:
            await repo.update(sample_transaction)

        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_status(self, mock_session, sample_orm):
        """Test updating transaction status."""
        repo = TransactionRepository(mock_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_orm
        mock_session.execute.return_value = mock_result

        updated = await repo.update_status(
            sample_orm.id,
            TransactionStatus.COMPLETED,
            None
        )

        assert isinstance(updated, Transaction)
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_status_with_error_message(self, mock_session, sample_orm):
        """Test updating transaction status with error message."""
        repo = TransactionRepository(mock_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_orm
        mock_session.execute.return_value = mock_result

        updated = await repo.update_status(
            sample_orm.id,
            TransactionStatus.FAILED,
            "Insufficient funds"
        )

        assert isinstance(updated, Transaction)

    @pytest.mark.asyncio
    async def test_update_status_not_found(self, mock_session):
        """Test updating status of non-existent transaction."""
        repo = TransactionRepository(mock_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        with pytest.raises(ValueError) as exc_info:
            await repo.update_status(uuid4(), TransactionStatus.FAILED)

        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_list_by_filters_no_filters(self, mock_session, sample_orm):
        """Test listing transactions without filters."""
        repo = TransactionRepository(mock_session)

        orm_list = [sample_orm]
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = orm_list
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        transactions = await repo.list_by_filters()

        assert len(transactions) == 1
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_by_filters_with_status(self, mock_session, sample_orm):
        """Test listing transactions filtered by status."""
        repo = TransactionRepository(mock_session)

        orm_list = [sample_orm]
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = orm_list
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        transactions = await repo.list_by_filters(status=TransactionStatus.PENDING)

        assert len(transactions) == 1

    @pytest.mark.asyncio
    async def test_list_by_filters_with_dates(self, mock_session, sample_orm):
        """Test listing transactions filtered by date range."""
        repo = TransactionRepository(mock_session)

        orm_list = [sample_orm]
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = orm_list
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()

        transactions = await repo.list_by_filters(
            start_date=start_date,
            end_date=end_date
        )

        assert len(transactions) == 1

    @pytest.mark.asyncio
    async def test_list_by_filters_with_pagination(self, mock_session):
        """Test listing transactions with pagination."""
        repo = TransactionRepository(mock_session)

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        transactions = await repo.list_by_filters(limit=50, offset=10)

        assert len(transactions) == 0
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_count_by_status(self, mock_session):
        """Test counting transactions by status."""
        repo = TransactionRepository(mock_session)

        # Mock result rows
        mock_row1 = Mock()
        mock_row1.status = "pending"
        mock_row1.count = 5

        mock_row2 = Mock()
        mock_row2.status = "completed"
        mock_row2.count = 10

        mock_result = MagicMock()
        mock_result.all.return_value = [mock_row1, mock_row2]
        mock_session.execute.return_value = mock_result

        counts = await repo.count_by_status()

        assert counts["pending"] == 5
        assert counts["completed"] == 10
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_count_by_status_with_user_filter(self, mock_session):
        """Test counting transactions by status for specific user."""
        repo = TransactionRepository(mock_session)

        mock_row = Mock()
        mock_row.status = "pending"
        mock_row.count = 3

        mock_result = MagicMock()
        mock_result.all.return_value = [mock_row]
        mock_session.execute.return_value = mock_result

        counts = await repo.count_by_status(user_id="user-123")

        assert counts["pending"] == 3

    @pytest.mark.asyncio
    async def test_delete_transaction_found(self, mock_session, sample_orm):
        """Test deleting an existing transaction."""
        repo = TransactionRepository(mock_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_orm
        mock_session.execute.return_value = mock_result

        deleted = await repo.delete(sample_orm.id)

        assert deleted is True
        mock_session.delete.assert_called_once_with(sample_orm)
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_transaction_not_found(self, mock_session):
        """Test deleting a non-existent transaction."""
        repo = TransactionRepository(mock_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        deleted = await repo.delete(uuid4())

        assert deleted is False
        mock_session.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_to_entity_conversion(self, mock_session, sample_orm):
        """Test ORM to Entity conversion."""
        repo = TransactionRepository(mock_session)

        entity = repo._to_entity(sample_orm)

        assert isinstance(entity, Transaction)
        assert entity.id == sample_orm.id
        assert entity.user_id == sample_orm.user_id
        assert entity.recipient_phone == sample_orm.recipient_phone
        assert entity.amount == sample_orm.amount
        assert entity.currency == Currency.COP
        assert entity.status == TransactionStatus.PENDING
