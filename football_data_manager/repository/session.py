import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from football_data_manager.common.services.config.config_service import ConfigService

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
TRANSIENT_MESSAGES = (
    "connection was closed",
    "Connection reset by peer",
    "ConnectionDoesNotExistError",
    "server closed the connection unexpectedly",
    "connection is closed",
    "SSL connection has been closed unexpectedly",
)


def is_transient(exc: Exception) -> bool:
    """Check if an exception is a transient connection error."""
    msg = str(exc)
    return any(pattern in msg for pattern in TRANSIENT_MESSAGES)


class SessionFactory:
    """
    Async database session factory.

    Manages the AsyncEngine lifecycle and provides sessions via context manager.

    :ivar engine: SQLAlchemy async engine
    """

    engine: AsyncEngine

    def __init__(self, config_service: ConfigService):
        """
        Initialize the session factory.

        :param config_service: Configuration service for DB URL
        """
        self.engine = create_async_engine(
            config_service.db.sqlalchemy_url,
            pool_pre_ping=True,
            pool_recycle=300,
        )
        self._session_maker = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Create a database session with automatic commit/rollback.

        :return: AsyncSession instance
        """
        async with self._session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def check_connection(self) -> bool:
        """
        Check database connectivity.

        :return: True if connection successful
        """
        try:
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False