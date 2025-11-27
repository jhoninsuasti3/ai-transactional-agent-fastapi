"""Database connection and session management.

This module provides the database engine, session factory, and connection
management for the application using async SQLAlchemy.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from apps.orchestrator.core.config import settings

# Create async engine with connection pooling
engine: AsyncEngine = create_async_engine(
    settings.database_url_str,
    echo=settings.DATABASE_ECHO,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
    # Use NullPool for testing to avoid connection pool issues
    poolclass=NullPool if settings.DEBUG else None,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI to get database session.

    This function provides a database session that automatically handles
    commits and rollbacks. Use it with FastAPI's Depends() for automatic
    session management.

    Yields:
        AsyncSession: Database session with automatic transaction management

    Example:
        ```python
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
        ```
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db_context() -> AsyncSession:
    """Get a database session for use in context managers.

    Use this when you need manual control over the session lifecycle.

    Returns:
        AsyncSession: Database session

    Example:
        ```python
        async with get_db_context() as db:
            result = await db.execute(select(User))
            await db.commit()
        ```
    """
    return AsyncSessionLocal()


async def init_db() -> None:
    """Initialize database (create tables).

    WARNING: This creates all tables from scratch. Only use this for:
    - Testing environments
    - Initial development setup
    - Demo purposes

    In production, ALWAYS use Alembic migrations instead.

    Example:
        ```python
        # In tests
        await init_db()
        ```
    """
    from apps.orchestrator.infrastructure.persistence.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    """Drop all database tables.

    WARNING: This is destructive! Only use for testing.

    Example:
        ```python
        # In test teardown
        await drop_db()
        ```
    """
    from apps.orchestrator.infrastructure.persistence.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def close_db() -> None:
    """Close all database connections and dispose of the engine.

    Call this during application shutdown to cleanly close all connections.

    Example:
        ```python
        @app.on_event("shutdown")
        async def shutdown():
            await close_db()
        ```
    """
    await engine.dispose()


async def health_check() -> bool:
    """Check if database connection is healthy.

    Returns:
        bool: True if database is reachable, False otherwise

    Example:
        ```python
        @app.get("/health")
        async def health():
            db_healthy = await health_check()
            return {"database": "healthy" if db_healthy else "unhealthy"}
        ```
    """
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
            return True
    except Exception:
        return False
