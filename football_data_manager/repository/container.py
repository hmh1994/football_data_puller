from dependency_injector import containers, providers

from football_data_manager.common.services.config.config_service import ConfigService
from football_data_manager.repository.session import SessionFactory
from football_data_manager.repository.repositories.analytics import AnalyticsRepository
from football_data_manager.repository.repositories.awards import AwardRepository
from football_data_manager.repository.repositories.competitions import (
    CompetitionRepository,
)
from football_data_manager.repository.repositories.fixtures import FixtureRepository
from football_data_manager.repository.repositories.grounds import GroundRepository
from football_data_manager.repository.repositories.match_stats import (
    MatchStatRepository,
)
from football_data_manager.repository.repositories.matches import MatchRepository
from football_data_manager.repository.repositories.news import NewsRepository
from football_data_manager.repository.repositories.officials import OfficialRepository
from football_data_manager.repository.repositories.player_stats import (
    PlayerStatRepository,
)
from football_data_manager.repository.repositories.players import PlayerRepository
from football_data_manager.repository.repositories.seasons import SeasonRepository
from football_data_manager.repository.repositories.staffs import StaffRepository
from football_data_manager.repository.repositories.team_stats import (
    TeamStatRepository,
)
from football_data_manager.repository.repositories.teams import TeamRepository


class RepositoryContainer(containers.DeclarativeContainer):
    """DI container for all repositories."""

    config_service = providers.Dependency(instance_of=ConfigService)

    session_factory = providers.Singleton(
        SessionFactory,
        config_service=config_service,
    )

    analytics_repository = providers.Singleton(
        AnalyticsRepository, session_factory=session_factory
    )
    award_repository = providers.Singleton(
        AwardRepository, session_factory=session_factory
    )
    competition_repository = providers.Singleton(
        CompetitionRepository, session_factory=session_factory
    )
    fixture_repository = providers.Singleton(
        FixtureRepository, session_factory=session_factory
    )
    ground_repository = providers.Singleton(
        GroundRepository, session_factory=session_factory
    )
    match_stat_repository = providers.Singleton(
        MatchStatRepository, session_factory=session_factory
    )
    match_repository = providers.Singleton(
        MatchRepository, session_factory=session_factory
    )
    news_repository = providers.Singleton(
        NewsRepository, session_factory=session_factory
    )
    official_repository = providers.Singleton(
        OfficialRepository, session_factory=session_factory
    )
    player_stat_repository = providers.Singleton(
        PlayerStatRepository, session_factory=session_factory
    )
    player_repository = providers.Singleton(
        PlayerRepository, session_factory=session_factory
    )
    season_repository = providers.Singleton(
        SeasonRepository, session_factory=session_factory
    )
    staff_repository = providers.Singleton(
        StaffRepository, session_factory=session_factory
    )
    team_stat_repository = providers.Singleton(
        TeamStatRepository, session_factory=session_factory
    )
    team_repository = providers.Singleton(
        TeamRepository, session_factory=session_factory
    )
