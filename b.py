from asyncio import run
from datetime import timedelta
from typing import Dict

from football_data_manager.common.enums.period_enum import PeriodEnum
from football_data_manager.common.repositories import Base
from football_data_manager.common.repositories.competitions.competition_entity import (
    CompetitionEntity,
)
from football_data_manager.common.repositories.grounds.ground_entity import GroundEntity
from football_data_manager.common.repositories.player_stats.player_stat_entity import (
    PlayerStatEntity,
)
from football_data_manager.common.repositories.players.player_entity import PlayerEntity
from football_data_manager.common.repositories.repository_container import (
    CommonRepositoryContainer,
)
from football_data_manager.common.repositories.seasons.season_entity import SeasonEntity
from football_data_manager.common.repositories.team_stats.team_stat_entity import (
    TeamStatEntity,
)
from football_data_manager.common.repositories.teams.team_entity import TeamEntity
from football_data_manager.common.services.common_service_container import (
    CommonServiceContainer,
)
from football_data_manager.common.services.config.config_service import ConfigService
from football_data_manager.common.services.db.db_service import DbService
from football_data_manager.common.utils.type_helper.datetime_helper import (
    create_utc_now,
)
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
from football_data_manager.puller.services.pulselive_new.services.pulselive_new_team_stats_puller import (
    PulseliveNewTeamStatsPuller,
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
) -> list[PlayerEntity]:
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
        if season.year_start < 2024:  # TODO: Remove Filtering
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
                if not match:
                    continue
                matches[-1].append(match)
                if match.period == PeriodEnum.FULLTIME:
                    match_stat = await match_stat_puller.pull_match_stat(match)
                    match_stats[-1].append(match_stat)
    return fixtures, matches, match_stats


async def update_match(
    service_container: CommonServiceContainer,
    repository_container: CommonRepositoryContainer,
    webclient: PulseliveNewWebclient,
) -> Dict:
    """
    Update existing fixture and match data based on timing conditions.

    Implements three timing conditions:
    1. Pre-Match Updates (≤2 hours to kickoff): Update match data
    2. Live/Post-Match Updates (during and after match): Update match + match_stat data
    3. Started PREMATCH Updates (past kickoff but still PREMATCH): Update match + match_stat data

    Returns structured results with update counts and entities.
    """
    # Phase 1: Initialization & Setup
    print("Phase 1: Initializing services and repositories...")

    # Initialize repository services
    competition_repository = repository_container.competition_repository()
    season_repository = repository_container.season_repository()
    fixture_repository = repository_container.fixture_repository()
    match_repository = repository_container.match_repository()
    match_stat_repository = repository_container.match_stat_repository()

    # Get competition by Pulselive ID (8)
    competition = await competition_repository.read_by_pulselive_id(8)
    # Get seasons for competition
    seasons = await season_repository.read_by_competition(competition)
    seasons.sort(key=lambda s: s.year_start, reverse=True)
    current_season = seasons[0]  # Most recent season

    # Initialize puller services
    fixture_puller = PulseliveNewFixturePuller(repository_container, webclient)
    player_puller = PulseliveNewPlayerPuller(
        repository_container, webclient, service_container
    )
    match_puller = PulseliveNewMatchPuller(
        service_container, repository_container, webclient, player_puller
    )
    match_stat_puller = PulseliveNewMatchStatPuller(repository_container, webclient)

    print(
        f"Initialized for competition: {competition.name_en}, season: {current_season.year_start}"
    )

    # Phase 2: Database Query & Data Retrieval
    print("Phase 2: Retrieving existing fixtures and matches...")

    # Try to use read_by_season if implemented, otherwise fallback to read_all + filter
    try:
        existing_fixtures = await fixture_repository.read_by_season(current_season)
        existing_matches = await match_repository.read_by_season(current_season)
    except Exception as e:
        print(f"Warning: read_by_season not implemented, using fallback method - ${e}")
        all_fixtures = await fixture_repository.read_all()
        all_matches = await match_repository.read_all()

        existing_fixtures = [
            f for f in all_fixtures if f.season_id == current_season.id
        ]
        existing_matches = [m for m in all_matches if m.season_id == current_season.id]

    print(
        f"Found {len(existing_fixtures)} fixtures and {len(existing_matches)} matches"
    )

    # Phase 3: Time-based Filtering Logic
    print("Phase 3: Applying time-based filtering...")

    current_time = create_utc_now()
    two_hours = timedelta(hours=2)
    ten_minutes = timedelta(minutes=10)

    pre_match_fixtures = []
    live_post_match_matches = []
    prematch_started_matches = []

    for fixture in existing_fixtures:
        if not fixture.kickoff_time:
            continue

        time_to_kickoff = fixture.kickoff_time - current_time

        # Condition 1: ≤2 hours to kickoff (but future matches only)
        if timedelta(0) <= time_to_kickoff <= two_hours:
            pre_match_fixtures.append(fixture)
            print(
                f"Pre-match fixture found: {fixture.id}, kickoff in {time_to_kickoff}"
            )

        # Find associated match for conditions 2 and 3
        associated_match = next(
            filter(lambda m: m.fixture_id == fixture.id, existing_matches), None
        )

        if associated_match:
            # Condition 3: kickoff has passed and match still shows PREMATCH
            if (
                fixture.kickoff_time < current_time
                and associated_match.period == PeriodEnum.PREMATCH
            ):
                prematch_started_matches.append(associated_match)
                time_since_kickoff = current_time - fixture.kickoff_time
                print(
                    f"Started PREMATCH match found: {associated_match.id}, kickoff {time_since_kickoff} ago"
                )
            elif associated_match.clock is not None:
                # Condition 2: match started and within 10min post-match
                match_end_time = (
                    fixture.kickoff_time
                    + timedelta(minutes=associated_match.clock)
                    + ten_minutes
                )

                if fixture.kickoff_time < current_time < match_end_time:
                    live_post_match_matches.append(associated_match)
                    print(
                        f"Live/post-match found: {associated_match.id}, clock: {associated_match.clock}min"
                    )

    print(
        f"Found {len(pre_match_fixtures)} pre-match fixtures, {len(live_post_match_matches)} live/post-match matches, and {len(prematch_started_matches)} started PREMATCH matches"
    )

    # Phase 4: Pre-Match Updates (Condition 1)
    print("Phase 4: Processing pre-match updates...")

    updated_matches = []

    for fixture in pre_match_fixtures:
        try:
            print(f"Updating pre-match data for fixture {fixture.id}...")

            # TODO: Fixture updates temporarily disabled
            # Will be re-enabled when pull_fixture_by_id is implemented
            # fresh_fixture_data = await fixture_puller.pull_fixture_by_id(
            #     fixture.source_id, competition, current_season
            # )
            # if fresh_fixture_data:
            #     updated_fixture = await fixture_repository.update(fresh_fixture_data)

            # Pull fresh match data using existing fixture
            fresh_match = await match_puller.pull_match(
                fixture, competition, current_season
            )
            if fresh_match:
                updated_match = await match_repository.update(fresh_match)
                updated_matches.append(updated_match)
                print(f"Successfully updated pre-match data for fixture {fixture.id}")

        except Exception as e:
            print(f"Error updating pre-match data for fixture {fixture.id}: {e}")
            continue

    # Phase 5: Live/Post-Match Updates (Condition 2)
    print("Phase 5: Processing live/post-match updates...")

    updated_live_matches = []
    updated_match_stats = []

    for match in live_post_match_matches:
        try:
            print(f"Updating live/post-match data for match {match.id}...")

            # Get associated fixture
            fixture = await fixture_repository.read_by_id(match.fixture_id)
            if not fixture:
                print(f"Warning: Fixture not found for match {match.id}")
                continue

            # Pull fresh match data
            fresh_match = await match_puller.pull_match(
                fixture, competition, current_season
            )
            if fresh_match:
                updated_match = await match_repository.update(fresh_match)
                updated_live_matches.append(updated_match)

                print(
                    f"Pulling match stats for match {updated_match.id} (period: {updated_match.period})"
                )
                fresh_match_stat = await match_stat_puller.pull_match_stat(
                    updated_match
                )
                if fresh_match_stat:
                    updated_stat = await match_stat_repository.update(fresh_match_stat)
                    updated_match_stats.append(updated_stat)
                    print(
                        f"Successfully updated match stats for match {updated_match.id}"
                    )

                print(f"Successfully updated live/post-match data for match {match.id}")

        except Exception as e:
            print(f"Error updating live/post-match data for match {match.id}: {e}")
            continue

    # Phase 6: Started PREMATCH Updates (Condition 3)
    print("Phase 6: Processing started PREMATCH updates...")

    updated_prematch_started_matches = []
    updated_prematch_started_match_stats = []

    for match in prematch_started_matches:
        try:
            print(f"Updating started PREMATCH data for match {match.id}...")

            # Get associated fixture
            fixture = await fixture_repository.read_by_id(match.fixture_id)
            if not fixture:
                print(f"Warning: Fixture not found for match {match.id}")
                continue

            # Pull fresh match data
            fresh_match = await match_puller.pull_match(
                fixture, competition, current_season
            )
            if fresh_match:
                print(f"fresh_match: {fresh_match.period}")
                updated_match = await match_repository.update(fresh_match)
                updated_prematch_started_matches.append(updated_match)

                # Pull match stats - started matches likely have some data available
                print(
                    f"Pulling match stats for started PREMATCH match {updated_match.id} (period: {updated_match.period})"
                )
                try:
                    fresh_match_stat = await match_stat_puller.pull_match_stat(
                        updated_match
                    )
                    if fresh_match_stat:
                        updated_stat = await match_stat_repository.update(
                            fresh_match_stat
                        )
                        updated_prematch_started_match_stats.append(updated_stat)
                        print(
                            f"Successfully updated match stats for started PREMATCH match {updated_match.id}"
                        )
                except Exception as stat_error:
                    print(
                        f"Warning: Could not pull stats for started PREMATCH match {updated_match.id}: {stat_error}"
                    )

                print(
                    f"Successfully updated started PREMATCH data for match {match.id}"
                )

        except Exception as e:
            print(f"Error updating started PREMATCH data for match {match.id}: {e}")
            continue

    # Phase 7: Error Handling & Logging (integrated above with try-catch blocks)

    # Phase 8: Return Results
    print("Phase 8: Compiling results...")

    total_matches_updated = (
        len(updated_matches)
        + len(updated_live_matches)
        + len(updated_prematch_started_matches)
    )
    total_stats_updated = len(updated_match_stats) + len(
        updated_prematch_started_match_stats
    )

    print(f"Pre-match updates: {len(updated_matches)} matches")
    print(
        f"Live/post-match updates: {len(updated_live_matches)} matches, {len(updated_match_stats)} stats"
    )
    print(
        f"Started PREMATCH updates: {len(updated_prematch_started_matches)} matches, {len(updated_prematch_started_match_stats)} stats"
    )
    print(
        f"Total updates completed: {total_matches_updated} matches, {total_stats_updated} stats"
    )

    return {
        "pre_match": {"matches": updated_matches},  # fixtures temporarily excluded
        "live_post_match": {
            "matches": updated_live_matches,
            "match_stats": updated_match_stats,
        },
        "started_prematch": {
            "matches": updated_prematch_started_matches,
            "match_stats": updated_prematch_started_match_stats,
        },
        "summary": {
            "total_matches_updated": total_matches_updated,
            "total_stats_updated": total_stats_updated,
        },
    }


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


async def create_team_stats(
    repository_container: CommonRepositoryContainer,
    webclient: PulseliveNewWebclient,
) -> list[TeamStatEntity]:
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
    team_stat_puller = PulseliveNewTeamStatsPuller(repository_container, webclient)
    team_stat_repository = repository_container.team_stat_repository()
    ground_repository = repository_container.ground_repository()
    team_stats = []
    for season in seasons:
        season_team_stats = []
        if season.year_start < 2024 or season.year_start >= 2025:
            continue
        teams = await webclient.get_v1_teams(
            competition_id=competition.source_id, season_id=season.season_source_id
        )
        for team in teams.data:
            team_entity = await team_repository.read_by_pulselive_id(str(team.id))
            ground_entity = await ground_repository.read_by_name_en(team.stadium.name)
            team_stat = await team_stat_puller.pull_team_stats(
                team_entity, competition, season, ground_entity
            )
            if team_stat:
                season_team_stats.append(team_stat)
        if season_team_stats:
            for team_stat in season_team_stats:
                team_stat = await team_stat_repository.update_position(
                    team_stat, season_team_stats
                )
                await team_stat_repository.update(team_stat)
                team_stats.append(team_stat)
    return team_stats


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
    # await create_player_stats(repository_container, webclient_service)
    # await create_team_stats(repository_container, webclient_service)
    await create_match(
        service_container,
        repository_container,
        webclient_service,
    )
    # await update_match(
    #     service_container,
    #     repository_container,
    #     webclient_service,
    # )
    # await create_news(config_service, db_service)
    # await update_match(service_container, repository_container, webclient_service)


run(runrun())
