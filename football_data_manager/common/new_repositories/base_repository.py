from asyncio import gather
from typing import TypeVar, Generic, Type, Callable, Coroutine

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from football_data_manager.common.enums.source_enum import SourceEnum
from football_data_manager.common.new_repositories.base_entity import BaseEntity
from football_data_manager.common.services.db.db_service import DbService
from football_data_manager.common.utils.type_helper.datetime_helper import (
    create_utc_now,
)
from football_data_manager.common.utils.type_helper.list_helper import remove_duplicates

TEntity = TypeVar("TEntity", bound=BaseEntity)


class BaseRepository(Generic[TEntity]):
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
    async def create(self, session: AsyncSession, entity: TEntity) -> TEntity | None:
        """
        Creates an entity in the database.
        :param session: Database session.
        :param entity: Entity to create.
        :return: Created entity or None if it is a duplicate.
        """
        if await self.__sieve_duplication(session, entity) is None:
            return None
        else:
            session.add(entity)
            await session.flush()
            await session.refresh(entity)
            return entity

    @with_db_session
    async def create_all(
        self,
        session: AsyncSession,
        entities: list[TEntity],
    ) -> list[TEntity]:
        """
        Creates multiple entities in the database.
        :param session: Database session.
        :param entities: Entities to create.
        If None, the duplicate entities will cause an error.
        :return: Created entities.
        """
        unduplicated_entities = remove_duplicates(
            remove_duplicates(entities, key=lambda e: e.id),
            key=lambda e: (e.source, e.source_id),
        )
        sieved_entities = await gather(
            *[self.__sieve_duplication(entity) for entity in unduplicated_entities]
        )
        candidate_entities = [e for e in sieved_entities if e is not None]
        if len(candidate_entities) > 0:
            session.add_all(candidate_entities)
            await session.flush()
        return candidate_entities

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
    async def read_by_id(self, session: AsyncSession, entity_id: str) -> TEntity | None:
        """
        Reads an entity by ID from the database.
        :param session: Database session.
        :param entity_id: Entity ID.
        :return: An entity or None if not found.
        """
        return await session.get(self.model, entity_id)

    @with_db_session
    async def read_by_source_id(
        self, session: AsyncSession, source: SourceEnum, source_id: str
    ) -> TEntity | None:
        """
        Reads an entity by source ID from the database.
        :param session: Database session.
        :param source: Source of the entity.
        :param source_id: Source ID.
        :return: An entity or None if not found.
        """
        stmt = (
            select(self.model)
            .filter_by(source=source.value.upper())
            .filter_by(source_id=source_id)
        )
        result = await session.execute(stmt)
        return result.scalars().first()

    @with_db_session
    async def update(self, session: AsyncSession, entity: TEntity) -> TEntity:
        """
        Updates an entity in the database.
        :param session: Database session.
        :param entity: Entity to update.
        :return: Updated entity.
        """
        now = create_utc_now()
        entity.updated_at = now
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

    @with_db_session
    async def __sieve_duplication(
        self, session: AsyncSession, entity: TEntity
    ) -> TEntity | None:
        """
        Sieves the duplication of the entity.
        :param session: Database session.
        :param entity: Entity to sieve.
        :return: Entity if not duplicated, None otherwise.
        """
        if await session.get(self.model, entity.id):
            return None
        else:
            return entity
