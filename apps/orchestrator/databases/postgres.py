"""PostgreSQL database configuration and session management.

Enterprise-grade database configuration with connection pooling,
async support, and proper lifecycle management.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool, QueuePool

from apps.orchestrator.settings import settings


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


class DatabaseManager:
    """Manages database engine and session lifecycle.

    This class provides centralized database connection management
    with support for different configurations based on environment.
    """

    def __init__(self) -> None:
        """Initialize database manager."""
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    def get_engine(self) -> AsyncEngine:
        """Get or create async database engine.

        Returns:
            AsyncEngine: SQLAlchemy async engine

        Example:
            >>> manager = DatabaseManager()
            >>> engine = manager.get_engine()
        """
        if self._engine is None:
            # Use NullPool for testing, QueuePool for production
            poolclass = NullPool if settings.ENVIRONMENT == "test" else QueuePool

            self._engine = create_async_engine(
                settings.database_url_str,
                echo=settings.DATABASE_ECHO,
                pool_size=settings.DATABASE_POOL_SIZE,
                max_overflow=settings.DATABASE_MAX_OVERFLOW,
                pool_pre_ping=True,  # Verify connections before using
                poolclass=poolclass,
                # Connection arguments
                connect_args={
                    "server_settings": {
                        "application_name": settings.OTEL_SERVICE_NAME,
                    },
                },
            )

        return self._engine

    def get_session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Get or create session factory.

        Returns:
            async_sessionmaker: Session factory for creating async sessions
        """
        if self._session_factory is None:
            engine = self.get_engine()
            self._session_factory = async_sessionmaker(
                engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )

        return self._session_factory

    async def close(self) -> None:
        """Close database connections and dispose engine."""
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Context manager for database sessions.

        Yields:
            AsyncSession: Database session

        Example:
            >>> async with manager.session() as session:
            ...     result = await session.execute(select(User))
        """
        session_factory = self.get_session_factory()
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


# Global database manager instance
db_manager = DatabaseManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions.

    Yields:
        AsyncSession: Database session

    Example:
        >>> @router.get("/users")
        ... async def get_users(db: AsyncSession = Depends(get_db)):
        ...     result = await db.execute(select(User))
        ...     return result.scalars().all()
    """
    async with db_manager.session() as session:
        yield session


async def init_db() -> None:
    """Initialize database (create tables).

    Note:
        This is mainly for testing. In production, use Alembic migrations.
    """
    engine = db_manager.get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close all database connections.

    Should be called on application shutdown.
    """
    await db_manager.close()