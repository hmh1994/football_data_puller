from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar, Self

from football_data_manager.common.new_repositories import Base
from football_data_manager.common.new_repositories.base_repository import BaseRepository
from football_data_manager.common.services.db.db_service import DbService

TRepository = TypeVar("TRepository", bound=BaseRepository)
TEntity = TypeVar("TEntity", bound=Base)
TId = TypeVar("TId")


class AbstractSampleData(Generic[TRepository, TEntity, TId], metaclass=ABCMeta):
    """
    Abstract sample data for repository classes.
    """

    @property
    @abstractmethod
    def prerequisites(self) -> list[type[Self]]:
        """
        List of prerequisite sample data classes.
        """
        pass

    @property
    @abstractmethod
    def entity_list(self) -> list[TEntity]:
        """
        List of entities for testing.
        """
        pass

    @staticmethod
    @abstractmethod
    def repository_instance(db_service: DbService) -> TRepository:
        """
        Creates a repository instance for testing.
        :param db_service: Pytest database service fixture.
        :return: Repository instance.
        """
        pass

    @staticmethod
    @abstractmethod
    def random_id() -> TId:
        """
        Creates a random ID for testing.
        :return: Random ID.
        """
        pass

    async def initialize(
        self, db_service: DbService, add_entity: bool = False
    ) -> list[TEntity]:
        """
        Initializes the sample data.
        :param db_service: Pytest database service fixture.
        :param add_entity: Whether to add the entity to the database.
        :return: List of entities for testing.
        """
        for prerequisite in self.prerequisites:
            prerequisite_instance = prerequisite()
            await prerequisite_instance.initialize(db_service, True)
        if add_entity:
            async with db_service.create_db_session() as session:
                for entity in self.entity_list:
                    if await session.get(entity.__class__, entity.id) is None:
                        session.add(entity)
                await session.commit()
        return self.entity_list
