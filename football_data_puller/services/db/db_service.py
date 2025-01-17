from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker

from football_data_puller.services.config.config_service import ConfigService


class DbService:
    """
    Database service class to handle database operations.
    :param config_service: Configuration service.
    :ivar engine: Database engine.
    """

    engine: AsyncEngine
    __session_maker: sessionmaker

    def __init__(self, config_service: ConfigService):
        self.engine = create_async_engine(
            config_service.db.sqlalchemy_url, pool_pre_ping=True
        )
        # noinspection PyTypeChecker
        self.__session_maker = sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def check_connection(self) -> bool:
        """
        Checks the database connection.
        :return: True if the connection is successful, False otherwise.
        """
        # noinspection PyBroadException
        try:
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    @asynccontextmanager
    async def create_db_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Creates a database session.
        :return: Database session.
        """
        async with self.__session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
