from sqlalchemy.orm import DeclarativeBase

from football_data_manager.common.old_repositories import Base
from football_data_manager.common.old_repositories.grounds.ground_entity import (
    GroundEntity,
)
from football_data_manager.common.old_repositories.grounds.ground_repository import (
    GroundRepository,
)
from tests.common.repositories.abstract_test_repository import AbstractTestRepository
from tests.common.repositories.sample_data.ground_sample_data import GroundSampleData


class TestGroundRepository(AbstractTestRepository[GroundRepository, GroundEntity]):
    """
    Test cases for GroundRepository class.
    """

    __test__ = True

    @property
    def base(self) -> DeclarativeBase:
        return Base

    @property
    def sample_data(self) -> GroundSampleData:
        return GroundSampleData()
