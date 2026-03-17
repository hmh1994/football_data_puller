from __future__ import annotations

from pathlib import Path

from football_data_manager.common.services.config.config_service import ConfigService
from football_data_manager.common.utils.constants import CONFIG_PATH
from football_data_manager.repository.container import RepositoryContainer
from football_data_manager.repository.session import SessionFactory
from football_data_manager.validator.cross_dataset import CrossDatasetValidator
from football_data_manager.validator.validators.analytics import AnalyticsValidator
from football_data_manager.validator.validators.award import AwardValidator
from football_data_manager.validator.validators.base import AbstractValidator
from football_data_manager.validator.validators.competition import CompetitionValidator
from football_data_manager.validator.validators.fixture import FixtureValidator
from football_data_manager.validator.validators.match import MatchValidator
from football_data_manager.validator.validators.match_stat import MatchStatValidator
from football_data_manager.validator.validators.news import NewsValidator
from football_data_manager.validator.validators.player import PlayerValidator
from football_data_manager.validator.validators.player_stat import PlayerStatValidator
from football_data_manager.validator.validators.season import SeasonValidator
from football_data_manager.validator.validators.team_stat import TeamStatValidator


class ValidatorContainer:
    """Factory container for validators."""

    def __init__(self, session_factory: SessionFactory):
        self._session_factory = session_factory

    def create_validator(self, entity: str) -> AbstractValidator:
        builders: dict[str, type[AbstractValidator]] = {
            "competition": CompetitionValidator,
            "season": SeasonValidator,
            "player": PlayerValidator,
            "fixture": FixtureValidator,
            "match": MatchValidator,
            "match-stat": MatchStatValidator,
            "team-stat": TeamStatValidator,
            "player-stat": PlayerStatValidator,
            "analytics": AnalyticsValidator,
            "news": NewsValidator,
            "award": AwardValidator,
            "cross-dataset": CrossDatasetValidator,
        }
        validator_cls = builders[entity]
        return validator_cls(session_factory=self._session_factory)


async def create_validator_container(
    config_path: Path = CONFIG_PATH,
) -> ValidatorContainer:
    """Build validator container with database session factory."""
    config_service = ConfigService(config_path)
    repository_container = RepositoryContainer(config_service=config_service)
    return ValidatorContainer(session_factory=repository_container.session_factory())
