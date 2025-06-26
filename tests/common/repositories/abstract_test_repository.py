from abc import ABCMeta, abstractmethod
from copy import copy
from random import choice
from typing import TypeVar, Generic, Type

from pytest import mark
from pytest_asyncio import fixture
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase

from football_data_manager.common.old_repositories import Base
from football_data_manager.common.old_repositories.base_repository import BaseRepository
from football_data_manager.common.services.db.db_service import DbService
from tests.common.repositories.sample_data.abstract_sample_data import (
    AbstractSampleData,
)
from tests.common.services.mocks import gen_db_service_mock
from tests.common.utils.random import random_string

TRepository = TypeVar("TRepository", bound=BaseRepository)
TEntity = TypeVar("TEntity", bound=Base)


class AbstractTestRepository(Generic[TRepository, TEntity], metaclass=ABCMeta):
    """
    Abstract test cases for repository classes.
    """

    __test__ = False

    @property
    @abstractmethod
    def base(self) -> Type[DeclarativeBase]:
        """
        Base class for the repository.
        """
        pass

    @property
    @abstractmethod
    def sample_data(self) -> AbstractSampleData:
        """
        Sample data class for the repository.
        """
        pass

    @fixture
    async def db_service(self) -> DbService:
        """
        Creates a DbService instance.
        :return: DbService instance with an in-memory database.
        """
        return gen_db_service_mock()

    @fixture
    async def repository(self, db_service: DbService) -> TRepository:
        """
        Creates a BaseRepository instance.
        :param db_service: Pytest database service fixture.
        :return: Repository instance for testing.
        """
        async with db_service.engine.begin() as connection:
            await connection.run_sync(self.base.metadata.drop_all)
            await connection.run_sync(self.base.metadata.create_all)
        return self.sample_data.repository_instance(db_service)

    @staticmethod
    def check_entity(entity: TEntity, fetched_entity: TEntity | None):
        """
        Checks if the entity and fetched entity are the same.
        :param entity: Entity to compare.
        :param fetched_entity: Fetched entity to compare.
        """
        assert type(fetched_entity) is type(entity), "Entity type mismatch."
        # noinspection PyTypeChecker
        for column in entity.__table__.columns:
            assert getattr(fetched_entity, column.name) == getattr(
                entity, column.name
            ), (
                f"Entity {column.name} mismatch (expected: {getattr(entity, column.name)}, "
                + f"actual: {getattr(fetched_entity, column.name)})."
            )

    @mark.asyncio
    async def test_create(self, db_service: DbService, repository: TRepository):
        """
        Tests the create method of BaseRepository.
        :param db_service: Pytest database service fixture.
        :param repository: Pytest repository fixture.
        """
        entity = (await self.sample_data.initialize(db_service))[0]
        result = await repository.create(entity)
        assert result == entity, "Entity creation failed."
        async with db_service.create_db_session() as session:
            fetched_entity = await session.get(repository.model, entity.id)
            self.check_entity(entity, fetched_entity)

    @mark.asyncio
    async def test_read_all(self, db_service: DbService, repository: TRepository):
        """
        Tests the read_all method of BaseRepository.
        :param db_service: Pytest database service fixture.
        :param repository: Pytest repository fixture.
        """
        entities = await self.sample_data.initialize(db_service, add_entity=True)
        fetched_entities = await repository.read_all()
        assert len(fetched_entities) == len(
            entities
        ), f"Entity count mismatch (expected: {len(entities)}, actual: {len(fetched_entities)})."
        for entity, fetched_entity in zip(entities, fetched_entities):
            self.check_entity(entity, fetched_entity)

    @mark.asyncio
    async def test_read_by_id(self, db_service: DbService, repository: TRepository):
        """
        Tests the read_by_id method of BaseRepository.
        :param db_service: Pytest database service fixture.
        :param repository: Pytest repository fixture.
        """
        entities = await self.sample_data.initialize(db_service, add_entity=True)
        for entity in entities:
            fetched_entity = await repository.read_by_id(entity.id)
            self.check_entity(entity, fetched_entity)

    @mark.asyncio
    async def test_read_by_id_not_found(
        self, db_service: DbService, repository: TRepository
    ):
        """
        Tests the read_by_id method of BaseRepository with an entity not found.
        :param db_service: Pytest database service fixture.
        :param repository: Pytest repository fixture.
        """
        random_id = self.sample_data.random_id()
        result = await repository.read_by_id(random_id)
        assert result is None, "Entity found unexpectedly."

    @mark.asyncio
    async def test_update(self, db_service: DbService, repository: TRepository):
        """
        Tests the update method of BaseRepository.
        :param db_service: Pytest database service fixture.
        :param repository: Pytest repository fixture.
        """
        entity = (await self.sample_data.initialize(db_service, add_entity=True))[0]
        columns = [
            col
            for col in entity.__table__.columns
            if isinstance(col.type, String) and col.name != "id"
        ]
        update_column = choice(columns)
        copied_entity = copy(entity)
        updated_value = random_string(20)
        while updated_value == getattr(entity, update_column.name):
            updated_value = random_string(20)
        setattr(copied_entity, update_column.name, updated_value)
        result = await repository.update(copied_entity)
        assert (
            result.id == entity.id == copied_entity.id
        ), f"Entity ID mismatch (expected: {entity.id}, actual: {result.id})."
        assert (
            getattr(result, update_column.name)
            == getattr(copied_entity, update_column.name)
            != getattr(entity, update_column.name)
        ), (
            f"Entity {update_column.name} mismatch "
            + f"(expected: {getattr(copied_entity, update_column.name)}, "
            + f"actual: {getattr(result, update_column.name)})."
        )
        async with db_service.create_db_session() as session:
            fetched_entity = await session.get(repository.model, entity.id)
            self.check_entity(result, fetched_entity)

    @mark.asyncio
    async def test_delete(self, db_service: DbService, repository: TRepository):
        """
        Tests the delete method of BaseRepository.
        :param db_service: Pytest database service fixture.
        :param repository: Pytest repository fixture.
        """
        entity = (await self.sample_data.initialize(db_service, add_entity=True))[0]
        await repository.delete(entity)
        async with db_service.create_db_session() as session:
            fetched_entity = await session.get(repository.model, entity.id)
            assert fetched_entity is None, "Entity deletion failed."
