from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import (
    Singleton,
    Dependency,
)

from football_data_manager.common.old_repositories.competitions.competition_repository import (
    CompetitionRepository,
)
from football_data_manager.common.old_repositories.fixtures.fixture_repository import (
    FixtureRepository,
)
from football_data_manager.common.old_repositories.grounds.ground_repository import (
    GroundRepository,
)
from football_data_manager.common.old_repositories.news.news_repository import (
    NewsRepository,
)
from football_data_manager.common.old_repositories.player_stats.player_stat_repository import (
    PlayerStatRepository,
)
from football_data_manager.common.old_repositories.players.player_repository import (
    PlayerRepository,
)
from football_data_manager.common.old_repositories.seasons.season_repository import (
    SeasonRepository,
)
from football_data_manager.common.old_repositories.team_stats.team_stat_repository import (
    TeamStatRepository,
)
from football_data_manager.common.old_repositories.teams.team_repository import (
    TeamRepository,
)
from football_data_manager.common.services.db.db_service import DbService


class CommonRepositoryContainer(DeclarativeContainer):
    """ """

    db_service = Dependency(instance_of=DbService)

    competition_repository = Singleton(CompetitionRepository, db_service=db_service)
    fixture_repository = Singleton(FixtureRepository, db_service=db_service)
    ground_repository = Singleton(GroundRepository, db_service=db_service)
    news_repository = Singleton(NewsRepository, db_service=db_service)
    player_stat_repository = Singleton(PlayerStatRepository, db_service=db_service)
    player_repository = Singleton(PlayerRepository, db_service=db_service)
    season_repository = Singleton(SeasonRepository, db_service=db_service)
    team_stat_repository = Singleton(TeamStatRepository, db_service=db_service)
    team_repository = Singleton(TeamRepository, db_service=db_service)
