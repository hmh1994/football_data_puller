from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import (
    Singleton,
    Dependency,
)

from football_data_manager.common.repositories.awards.award_repository import (
    AwardRepository,
)
from football_data_manager.common.repositories.competitions.competition_repository import (
    CompetitionRepository,
)
from football_data_manager.common.repositories.fixtures.fixture_repository import (
    FixtureRepository,
)
from football_data_manager.common.repositories.grounds.ground_repository import (
    GroundRepository,
)
from football_data_manager.common.repositories.match_stats.match_stat_repository import (
    MatchStatRepository,
)
from football_data_manager.common.repositories.matches.match_repository import (
    MatchRepository,
)
from football_data_manager.common.repositories.news.news_repository import (
    NewsRepository,
)
from football_data_manager.common.repositories.officials.official_repository import (
    OfficialRepository,
)
from football_data_manager.common.repositories.player_stats.player_stat_repository import (
    PlayerStatRepository,
)
from football_data_manager.common.repositories.players.player_repository import (
    PlayerRepository,
)
from football_data_manager.common.repositories.seasons.season_repository import (
    SeasonRepository,
)
from football_data_manager.common.repositories.staffs.staff_repository import (
    StaffRepository,
)
from football_data_manager.common.repositories.team_stats.team_stat_repository import (
    TeamStatRepository,
)
from football_data_manager.common.repositories.teams.team_repository import (
    TeamRepository,
)
from football_data_manager.common.services.db.db_service import DbService


class CommonRepositoryContainer(DeclarativeContainer):
    """
    Common repository container for the application.
    :ivar award_repository: Award repository.
    :ivar competition_repository: Competition repository.
    :ivar fixture_repository: Fixture repository.
    :ivar ground_repository: Ground repository.
    :ivar match_stat_repository: Match statistics repository.
    :ivar match_repository: Match repository.
    :ivar news_repository: News repository.
    :ivar official_repository: Official repository.
    :ivar player_stat_repository: Player statistics repository.
    :ivar player_repository: Player repository.
    :ivar season_repository: Season repository.
    :ivar staff_repository: Staff repository.
    :ivar team_stat_repository: Team statistics repository.
    :ivar team_repository: Team repository.
    """

    db_service = Dependency(instance_of=DbService)

    award_repository = Singleton(AwardRepository, db_service=db_service)
    competition_repository = Singleton(CompetitionRepository, db_service=db_service)
    fixture_repository = Singleton(FixtureRepository, db_service=db_service)
    ground_repository = Singleton(GroundRepository, db_service=db_service)
    match_stat_repository = Singleton(MatchStatRepository, db_service=db_service)
    match_repository = Singleton(MatchRepository, db_service=db_service)
    news_repository = Singleton(NewsRepository, db_service=db_service)
    official_repository = Singleton(OfficialRepository, db_service=db_service)
    player_stat_repository = Singleton(PlayerStatRepository, db_service=db_service)
    player_repository = Singleton(PlayerRepository, db_service=db_service)
    season_repository = Singleton(SeasonRepository, db_service=db_service)
    staff_repository = Singleton(StaffRepository, db_service=db_service)
    team_stat_repository = Singleton(
        TeamStatRepository, db_service=db_service, match_repository=match_repository
    )
    team_repository = Singleton(TeamRepository, db_service=db_service)
