from sqlalchemy.orm import DeclarativeBase

from football_data_puller.repositories import Base
from football_data_puller.repositories.competitions.competition_entity import (
    CompetitionEntity,
)
from football_data_puller.repositories.competitions.competition_repository import (
    CompetitionRepository,
)
from tests.repositories.abstract_test_repository import AbstractTestRepository
from tests.repositories.sample_data.competition_sample_data import CompetitionSampleData


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
