from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import (
    Configuration,
    DependenciesContainer,
    Singleton,
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
from football_data_manager.common.repositories.players.player_repository import (
    PlayerRepository,
)
from football_data_manager.common.repositories.seasons.season_repository import (
    SeasonRepository,
)
from football_data_manager.common.repositories.standings.standing_repository import (
    StandingRepository,
)
from football_data_manager.common.repositories.teams.team_repository import (
    TeamRepository,
)


class CommonRepositoryContainer(DeclarativeContainer):
    """
    Common repository container for the application.
    :ivar container_config: Container's configuration.
    :ivar services: Services container.
    :ivar competition_repository: Competition repository.
    :ivar fixture_repository: Fixture repository.
    :ivar ground_repository: Ground repository.
    :ivar player_repository: Player repository.
    :ivar season_repository: Season repository.
    :ivar standing_repository: Standing repository.
    :ivar team_repository: Team repository.
    """

    container_config = Configuration()
    services = DependenciesContainer()

    competition_repository = Singleton(
        CompetitionRepository, db_service=services.db_service
    )
    fixture_repository = Singleton(FixtureRepository, db_service=services.db_service)
    ground_repository = Singleton(GroundRepository, db_service=services.db_service)
    player_repository = Singleton(PlayerRepository, db_service=services.db_service)
    season_repository = Singleton(SeasonRepository, db_service=services.db_service)
    standing_repository = Singleton(StandingRepository, db_service=services.db_service)
    team_repository = Singleton(TeamRepository, db_service=services.db_service)
