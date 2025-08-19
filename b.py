from asyncio import run

from football_data_manager.common.enums.period_enum import PeriodEnum
from football_data_manager.common.repositories import Base
from football_data_manager.common.repositories.competitions.competition_entity import (
    CompetitionEntity,
)
from football_data_manager.common.repositories.grounds.ground_entity import GroundEntity
from football_data_manager.common.repositories.player_stats.player_stat_entity import (
    PlayerStatEntity,
)
from football_data_manager.common.repositories.repository_container import (
    CommonRepositoryContainer,
)
from football_data_manager.common.repositories.seasons.season_entity import SeasonEntity
from football_data_manager.common.repositories.teams.team_entity import TeamEntity
from football_data_manager.common.services.common_service_container import (
    CommonServiceContainer,
)
from football_data_manager.common.services.config.config_service import ConfigService
from football_data_manager.common.services.db.db_service import DbService
from football_data_manager.puller.services.pulselive_new.components.pulselive_new_webclient import (
    PulseliveNewWebclient,
)
from football_data_manager.puller.services.pulselive_new.services.pulselive_new_competition_puller import (
    PulseliveNewCompetitionPuller,
)
from football_data_manager.puller.services.pulselive_new.services.pulselive_new_fixture_puller import (
    PulseliveNewFixturePuller,
)
from football_data_manager.puller.services.pulselive_new.services.pulselive_new_match_puller import (
    PulseliveNewMatchPuller,
)
from football_data_manager.puller.services.pulselive_new.services.pulselive_new_match_stat_puller import (
    PulseliveNewMatchStatPuller,
)
from football_data_manager.puller.services.pulselive_new.services.pulselive_new_player_puller import (
    PulseliveNewPlayerPuller,
)
from football_data_manager.puller.services.pulselive_new.services.pulselive_new_player_stats_puller import (
    PulseliveNewPlayerStatsPuller,
)
from football_data_manager.puller.services.pulselive_new.services.pulselive_new_season_puller import (
    PulseliveNewSeasonPuller,
)
from football_data_manager.puller.services.pulselive_new.services.pulselive_new_team_puller import (
    PulseliveNewTeamPuller,
)
from football_data_manager.puller.services.the_athletic.the_athletic_puller_service import (
    TheAthleticPullerService,
)


async def create_competitions(
    service_container: CommonServiceContainer,
    repository_container: CommonRepositoryContainer,
    webclient: PulseliveNewWebclient,
) -> list[CompetitionEntity]:
    competition_puller = PulseliveNewCompetitionPuller(
        service_container, repository_container, webclient
    )
    competitions = await competition_puller.pull_all_competitions()
    return competitions


async def create_seasons(
    repository_container: CommonRepositoryContainer,
    webclient: PulseliveNewWebclient,
) -> list[list[SeasonEntity]]:
    competition_repository = repository_container.competition_repository()
    competitions = await competition_repository.read_all()
    if not competitions:
        return []
    seasons = []
    season_puller = PulseliveNewSeasonPuller(repository_container, webclient)
    for competition in competitions:
        seasons.append(await season_puller.pull_seasons_for_competition(competition))
    return seasons


async def create_teams_and_grounds(
    service_container: CommonServiceContainer,
    repository_container: CommonRepositoryContainer,
    webclient: PulseliveNewWebclient,
) -> tuple[list[TeamEntity], list[GroundEntity]]:
    competition_repository = repository_container.competition_repository()
    competition = await competition_repository.read_by_pulselive_id(8)
    if not competition:
        return [], []
    season_repository = repository_container.season_repository()
    seasons = await season_repository.read_all()
    if not seasons:
        return [], []
    seasons.sort(key=lambda s: s.year_start, reverse=True)
    teams = []
    grounds = []
    team_puller = PulseliveNewTeamPuller(
        repository_container, webclient, service_container
    )
    for season in seasons:
        if season.competition_id != competition.id:
            continue
        team, ground = await team_puller.pull_teams_for_season(competition, season)
        if team:
            teams.extend(team)
        if ground:
            grounds.extend(ground)
    return teams, grounds


async def create_players(
    service_container: CommonServiceContainer,
    repository_container: CommonRepositoryContainer,
    webclient: PulseliveNewWebclient,
) -> list[TeamEntity]:
    competition_repository = repository_container.competition_repository()
    competition = await competition_repository.read_by_pulselive_id(8)
    if not competition:
        return []
    season_repository = repository_container.season_repository()
    seasons = await season_repository.read_by_competition(competition)
    if not seasons:
        return []
    seasons.sort(key=lambda s: s.year_start, reverse=True)
    team_repository = repository_container.team_repository()
    teams = await team_repository.read_all()
    if not teams:
        return []
    players = []
    squad_puller = PulseliveNewPlayerPuller(
        repository_container, webclient, service_container
    )
    for season in seasons:
        if season.year_start < 2024:  # TODO: Remove Filtering
            continue
        for team in teams:
            players.extend(
                await squad_puller.pull_players_for_team(competition, season, team)
            )
    return players


async def create_match(
    service_container: CommonServiceContainer,
    repository_container: CommonRepositoryContainer,
    webclient: PulseliveNewWebclient,
):
    competition_repository = repository_container.competition_repository()
    competition = await competition_repository.read_by_pulselive_id(8)
    if not competition:
        return []
    season_repository = repository_container.season_repository()
    seasons = await season_repository.read_by_competition(competition)
    if not seasons:
        return []
    seasons.sort(key=lambda s: s.year_start, reverse=True)
    fixture_puller = PulseliveNewFixturePuller(repository_container, webclient)
    player_puller = PulseliveNewPlayerPuller(
        repository_container, webclient, service_container
    )
    match_puller = PulseliveNewMatchPuller(
        service_container, repository_container, webclient, player_puller
    )
    match_stat_puller = PulseliveNewMatchStatPuller(repository_container, webclient)
    fixtures = []
    matches = []
    match_stats = []
    for season in seasons:
        if (
            season.year_start < 2024 or season.year_start >= 2025
        ):  # TODO: Remove Filtering
            continue
        for matchweek in range(1, 40):
            f = await fixture_puller.pull_fixtures(competition, season, matchweek)
            if not f:
                continue
            fixtures.extend(f)
            matches.append([])
            match_stats.append([])
            for fixture in f:
                match = await match_puller.pull_match(fixture, competition, season)
                matches[-1].append(match)
                if match.period == PeriodEnum.FULLTIME:
                    match_stat = await match_stat_puller.pull_match_stat(match)
                    match_stats[-1].append(match_stat)
    return fixtures, matches, match_stats


async def create_player_stats(
    repository_container: CommonRepositoryContainer,
    webclient: PulseliveNewWebclient,
) -> list[PlayerStatEntity]:
    competition_repository = repository_container.competition_repository()
    competition = await competition_repository.read_by_pulselive_id(8)
    if not competition:
        return []
    season_repository = repository_container.season_repository()
    seasons = await season_repository.read_by_competition(competition)
    if not seasons:
        return []
    seasons.sort(key=lambda s: s.year_start, reverse=True)
    player_repository = repository_container.player_repository()
    players = await player_repository.read_all()
    player_stats_puller = PulseliveNewPlayerStatsPuller(repository_container, webclient)
    player_stats = []
    for season in seasons:
        if season.year_start < 2024:
            continue
        for player in players:
            try:
                player_stat = await player_stats_puller.pull_player_stats(
                    player, competition, season
                )
                if player_stat:
                    player_stats.append(player_stat)
            except ValueError as e:
                print(f"Error pulling stats for player {player.id}: {e}")
            except Exception as e:
                raise RuntimeError(
                    f"Unexpected error pulling stats for player {player.id}: {e}"
                ) from e
    return player_stats


async def create_news(config_service: ConfigService, db_service: DbService):
    puller_service = TheAthleticPullerService(
        anthropic_config=config_service.api_list.anthropic,
        the_athletic_graphql_config=config_service.api_list.the_athletic_graphql,
        db_service=db_service,
    )
    await puller_service.pull_news()


async def runrun():
    service_container = CommonServiceContainer()
    service_container.container_config.from_dict({"config_path": "./configs/.env"})
    config_service = service_container.config_service()
    db_service = service_container.db_service()
    async with db_service.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    repository_container = CommonRepositoryContainer(db_service=db_service)
    webclient_service = PulseliveNewWebclient(config_service.api_list.pulselive_new)
    # await create_competitions(
    #     service_container,
    #     repository_container,
    #     webclient_service,
    # )
    # await create_seasons(repository_container, webclient_service)
    # await create_teams_and_grounds(
    #     service_container, repository_container, webclient_service
    # )
    # await create_players(service_container, repository_container, webclient_service)
    await create_player_stats(repository_container, webclient_service)
    # await create_match(
    #     service_container,
    #     repository_container,
    #     webclient_service,
    # )
    # await update_news(config_service, db_service)


run(runrun())
