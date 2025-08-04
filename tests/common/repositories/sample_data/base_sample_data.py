from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

from football_data_manager.common.repositories.base_entity import BaseEntity
from football_data_manager.common.repositories.base_repository import BaseRepository
from football_data_manager.common.services.db.db_service import DbService
from tests.common.repositories.sample_data.abstract_sample_data import (
    AbstractSampleData,
)
from tests.common.utils.random import random_number

FakeBase = declarative_base()


class EntityMock(BaseEntity):
    """
    Fake entity class for testing
    :ivar id: Entity ID.
    :ivar name: Entity name.
    """

    __tablename__ = "fakes"

    id = Column(Integer, primary_key=True)
    name = Column(String)


class BaseSampleData(AbstractSampleData[BaseRepository[EntityMock], EntityMock, int]):
    """
    Sample data for CompetitionRepository.
    """

    @property
    def prerequisites(self) -> list[type[AbstractSampleData]]:
        return []

    @property
    def entity_list(self) -> list[EntityMock]:
        return [
            EntityMock(id=1, name="test1"),
            EntityMock(id=2, name="test2"),
            EntityMock(id=3, name="test3"),
        ]

    @staticmethod
    def repository_instance(db_service: DbService) -> BaseRepository:
        return BaseRepository(db_service)

    @staticmethod
    def random_id() -> int:
        return random_number(4)
