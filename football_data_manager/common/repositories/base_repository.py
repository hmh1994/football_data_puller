from typing import TypeVar, Generic, Type, Callable, Coroutine

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from football_data_manager.common.repositories import Base
from football_data_manager.common.services.db.db_service import DbService

TEntity = TypeVar("TEntity", bound=Base)
TId = TypeVar("TId")


class BaseRepository(Generic[TEntity, TId]):
    """
    Base repository class to handle CRUD operations.
    :param db_service: Database service.
    :param model: Model class.
    """

    __db_service: DbService
    model: Type[TEntity]

    def __init__(self, db_service: DbService, model: Type[TEntity]):
        self.__db_service = db_service
        self.model = model

    @staticmethod
    def with_db_session(func: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        """
        Decorator to add a database session to the function.
        :param func: Function to decorate.
        :return: Decorated function.
        """

        async def wrapper(self, *args, **kwargs):
            assert (
                await self.__db_service.check_connection()
            ), "Database connection failed."
            async with self.__db_service.create_db_session() as session:
                return await func(self, session, *args, **kwargs)

        return wrapper

    @with_db_session
    async def create(self, session: AsyncSession, entity: TEntity) -> TEntity:
        """
        Creates an entity in the database.
        :param session: Database session.
        :param entity: Entity to create.
        :return: Created entity.
        """
        session.add(entity)
        await session.flush()
        await session.refresh(entity)
        return entity

    @with_db_session
    async def read_all(self, session: AsyncSession) -> list[TEntity]:
        """
        Reads all entities from the database.
        :param session: Database session.
        :return: List of entities.
        """
        result = await session.execute(select(self.model))
        return list(result.scalars().all())

    @with_db_session
    async def read_by_id(self, session: AsyncSession, entity_id: TId) -> TEntity:
        """
        Reads an entity by ID from the database.
        :param session: Database session.
        :param entity_id: Entity ID.
        :return: An entity.
        """
        return await session.get(self.model, entity_id)

    @with_db_session
    async def update(self, session: AsyncSession, entity: TEntity) -> TEntity:
        """
        Updates an entity in the database.
        :param session: Database session.
        :param entity: Entity to update.
        :return: Updated entity.
        """
        merged_entity = await session.merge(entity)
        await session.flush()
        await session.refresh(merged_entity)
        return merged_entity

    @with_db_session
    async def delete(self, session: AsyncSession, entity: TEntity):
        """
        Deletes an entity from the database.
        :param session: Database session.
        :param entity: Entity to delete.
        """
        real_entity = await session.get(self.model, entity.id)
        if real_entity is not None:
            await session.delete(real_entity)
            await session.flush()
