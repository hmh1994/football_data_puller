from sqlalchemy.orm import DeclarativeBase

from football_data_manager.common.new_repositories import Base
from football_data_manager.common.new_repositories.competitions.competition_repository import (
    CompetitionEntity,
    CompetitionRepository,
)
from tests.common.repositories.abstract_test_repository import AbstractTestRepository
from tests.common.repositories.sample_data.competition_sample_data import (
    CompetitionSampleData,
)


class TestCompetitionRepository(
    AbstractTestRepository[CompetitionRepository, CompetitionEntity]
):
    """
    Test cases for CompetitionRepository class.
    """

    __test__ = True

    @property
    def base(self) -> DeclarativeBase:
        return Base

    @property
    def sample_data(self) -> CompetitionSampleData:
        return CompetitionSampleData()
