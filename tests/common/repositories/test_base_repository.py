from sqlalchemy.orm import DeclarativeBase

from football_data_manager.common.repositories.base_repository import BaseRepository
from tests.common.repositories.abstract_test_repository import AbstractTestRepository
from tests.common.repositories.sample_data.base_sample_data import (
    EntityMock,
    FakeBase,
    BaseSampleData,
)


class TestBaseRepository(
    AbstractTestRepository[BaseRepository[EntityMock, int], EntityMock]
):
    """
    Test cases for BaseRepository class.
    """

    __test__ = True

    @property
    def base(self) -> DeclarativeBase:
        return FakeBase

    @property
    def sample_data(self) -> BaseSampleData:
        return BaseSampleData()
