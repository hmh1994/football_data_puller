from pytest import mark
from pytest_asyncio import fixture
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

from football_data_puller.repositories.base_repository import BaseRepository
from football_data_puller.services.db.db_service import DbService
from tests.services.mocks import gen_db_service_mock


class TestBaseRepository:
    """
    Test cases for BaseRepository class.
    :ivar base_mock: Base mock class.
    """

    base_mock = declarative_base()

    class EntityMock(base_mock):
        """
        Fake entity class for testing
        :ivar id: Entity ID.
        :ivar name: Entity name.
        """

        __tablename__ = "fakes"

        id = Column(Integer, primary_key=True)
        name = Column(String)

    @fixture
    async def db_service(self):
        """
        Creates a DbService instance.
        :return: DbService instance with an in-memory database.
        """
        return gen_db_service_mock()

    @fixture
    async def base_repository(self, db_service: DbService) -> BaseRepository:
        """
        Creates a BaseRepository instance.
        :param db_service: Pytest database service fixture.
        :return: BaseRepository instance with a fake entity.
        """
        async with db_service.engine.begin() as connection:
            await connection.run_sync(self.base_mock.metadata.drop_all)
            await connection.run_sync(self.base_mock.metadata.create_all)
        return BaseRepository(db_service, self.EntityMock)

    @staticmethod
    def __check_entity(entity: EntityMock, fetched_entity: EntityMock | None):
        """
        Checks if the entity and fetched entity are the same.
        :param entity: Entity to compare.
        :param fetched_entity: Fetched entity to compare.
        """
        assert fetched_entity is not None, "Entity not found in database."
        assert (
            fetched_entity.id == entity.id
        ), f"Entity ID mismatch (expected: {entity.id}, actual: {fetched_entity.id})."
        assert (
            fetched_entity.name == entity.name
        ), f"Entity name mismatch (expected: {entity.name}, actual: {fetched_entity.name})."

    @mark.asyncio
    async def test_create(self, db_service: DbService, base_repository: BaseRepository):
        """
        Tests the create method of BaseRepository.
        :param db_service: Pytest database service fixture.
        :param base_repository: Pytest base repository fixture.
        """
        entity = self.EntityMock(id=1, name="test")
        result = await base_repository.create(entity)
        assert result == entity, "Entity creation failed."
        async with db_service.create_db_session() as session:
            fetched_entity = await session.get(self.EntityMock, entity.id)
            self.__check_entity(entity, fetched_entity)

    @mark.asyncio
    async def test_read_all(
        self, db_service: DbService, base_repository: BaseRepository
    ):
        """
        Tests the read_all method of BaseRepository.
        :param db_service: Pytest database service fixture.
        :param base_repository: Pytest base repository fixture.
        """
        entities = [self.EntityMock(id=idx, name=f"test{idx}") for idx in range(1, 4)]
        for entity in entities:
            async with db_service.create_db_session() as session:
                session.add(entity)
                await session.commit()
        fetched_entities = await base_repository.read_all()
        assert len(fetched_entities) == len(
            entities
        ), f"Entity count mismatch (expected: {len(entities)}, actual: {len(fetched_entities)})."
        for entity, fetched_entity in zip(entities, fetched_entities):
            self.__check_entity(entity, fetched_entity)

    @mark.asyncio
    async def test_read_by_id(
        self, db_service: DbService, base_repository: BaseRepository
    ):
        """
        Tests the read_by_id method of BaseRepository.
        :param db_service: Pytest database service fixture.
        :param base_repository: Pytest base repository fixture.
        """
        entities = [self.EntityMock(id=idx, name=f"test{idx}") for idx in range(1, 4)]
        for entity in entities:
            async with db_service.create_db_session() as session:
                session.add(entity)
                await session.commit()
        for entity in entities:
            fetched_entity = await base_repository.read_by_id(entity.id)
            self.__check_entity(entity, fetched_entity)

    @mark.asyncio
    async def test_read_by_id_not_found(
        self, db_service: DbService, base_repository: BaseRepository
    ):
        """
        Tests the read_by_id method of BaseRepository with an entity not found.
        :param db_service: Pytest database service fixture.
        :param base_repository: Pytest base repository fixture.
        """
        result = await base_repository.read_by_id(0)
        assert result is None, "Entity found unexpectedly."

    @mark.asyncio
    async def test_update(self, db_service: DbService, base_repository: BaseRepository):
        """
        Tests the update method of BaseRepository.
        :param db_service: Pytest database service fixture.
        :param base_repository: Pytest base repository fixture.
        """
        entity = self.EntityMock(id=1, name="test")
        async with db_service.create_db_session() as session:
            session.add(entity)
            await session.commit()
        entity.name = "updated"
        result = await base_repository.update(entity)
        assert result == entity, "Entity update failed."
        async with db_service.create_db_session() as session:
            fetched_entity = await session.get(self.EntityMock, entity.id)
            self.__check_entity(entity, fetched_entity)

    @mark.asyncio
    async def test_delete(self, db_service: DbService, base_repository: BaseRepository):
        """
        Tests the delete method of BaseRepository.
        :param db_service: Pytest database service fixture.
        :param base_repository: Pytest base repository fixture.
        """
        entity = self.EntityMock(id=1, name="test")
        async with db_service.create_db_session() as session:
            session.add(entity)
            await session.commit()
        await base_repository.delete(entity)
        async with db_service.create_db_session() as session:
            fetched_entity = await session.get(self.EntityMock, entity.id)
            assert fetched_entity is None, "Entity deletion failed."
