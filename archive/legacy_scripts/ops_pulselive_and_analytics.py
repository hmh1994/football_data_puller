import math
from asyncio import run
from datetime import timedelta
from typing import Dict

from football_data_manager.common.enums.analytics_key_enum import AnalyticsKeyEnum
from football_data_manager.common.enums.period_enum import PeriodEnum
from football_data_manager.common.enums.source_enum import SourceEnum
from football_data_manager.common.repositories import Base
from football_data_manager.common.repositories.analytics.analytics_entity import (
    AnalyticsEntity,
)
from football_data_manager.common.repositories.analytics.analytics_repository import (
    AnalyticsRepository,
)
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
                fresh_match_stats = await match_stat_puller.pull_match_stat(
                    updated_match
                )
                if fresh_match_stats:
                    for fresh_match_stat in fresh_match_stats:
                        updated_stat = await match_stat_repository.update(
                            fresh_match_stat
                        )
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
                    fresh_match_stats = await match_stat_puller.pull_match_stat(
                        updated_match
                    )
                    if fresh_match_stats:
                        for fresh_match_stat in fresh_match_stats:
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
        if season.year_start < 2025:
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


async def create_award(
    service_container: CommonServiceContainer,
    repository_container: CommonRepositoryContainer,
    webclient: PulseliveNewWebclient,
):
    """
    Pull and create award data for the current season.

    Retrieves player and staff awards from PulseLive API and creates
    award entities with associations to player stats and staff entities.
    Persists all updated entities to database after processing.
    """
    from football_data_manager.puller.services.pulselive_new.services.pulselive_new_award_puller import (
        PulseliveNewAwardPuller,
    )

    competition_repository = repository_container.competition_repository()
    competition = await competition_repository.read_by_pulselive_id(8)
    if not competition:
        return []

    season_repository = repository_container.season_repository()
    seasons = await season_repository.read_by_competition(competition)
    if not seasons:
        return []

    seasons.sort(key=lambda s: s.year_start, reverse=True)

    award_puller = PulseliveNewAwardPuller(
        repository_container, webclient, service_container
    )

    player_stat_repository = repository_container.player_stat_repository()
    staff_repository = repository_container.staff_repository()

    for season in seasons:
        if season.year_start not in [2024, 2025]:
            continue

        print(f"Processing awards for season {season.year_start}...")

        awards, player_stats, staffs = await award_puller.pull_awards_for_season(
            competition, season
        )

        # Immediately persist this season's updates to database
        for player_stat in player_stats:
            await player_stat_repository.update(player_stat)

        for staff in staffs:
            await staff_repository.update(staff)

        print(
            f"✅ Season {season.year_start}: {len(awards)} awards, {len(player_stats)} player stats, {len(staffs)} staffs updated"
        )
    return None


async def create_news(config_service: ConfigService, db_service: DbService):
    puller_service = TheAthleticPullerService(
        anthropic_config=config_service.api_list.anthropic,
        the_athletic_graphql_config=config_service.api_list.the_athletic_graphql,
        db_service=db_service,
    )
    await puller_service.pull_news()


async def upsert_analytics(
    repository_container: CommonRepositoryContainer,
    db_service: DbService,
) -> list[AnalyticsEntity]:
    """
    Calculate and upsert analytics for all seasons with matches.

    Iterates through seasons from oldest to newest, calculates analytics
    metrics based on AnalyticsKeyEnum keys, and upserts them to the analytics table.
    Skips seasons without collected matches. Calculates delta as percentage change
    from the previous season's value.

    :param repository_container: Repository container for database operations
    :param db_service: Database service for analytics repository
    :returns: List of upserted analytics entities
    """
    print("=" * 80)
    print("Analytics Upsert Process")
    print("=" * 80)

    # Initialize repositories
    competition_repository = repository_container.competition_repository()
    season_repository = repository_container.season_repository()
    fixture_repository = repository_container.fixture_repository()
    match_repository = repository_container.match_repository()
    match_stat_repository = repository_container.match_stat_repository()
    analytics_repository = AnalyticsRepository(db_service)

    # Get competition and seasons
    competition = await competition_repository.read_by_pulselive_id(8)
    if not competition:
        print("Error: Competition not found")
        return []

    seasons = await season_repository.read_by_competition(competition)
    if not seasons:
        print("Error: No seasons found")
        return []

    # Sort from oldest to newest
    seasons.sort(key=lambda s: s.year_start)

    all_upserted_analytics = []
    # Store previous season values for delta calculation
    previous_values: Dict[AnalyticsKeyEnum, float] = {}

    for season in seasons:
        print(f"\nProcessing season {season.year_start}...")

        # Get fixtures for the season first
        fixtures = await fixture_repository.read_by_season(season)
        if not fixtures:
            print(f"  Skipping: No fixtures found for season {season.year_start}")
            continue

        # Get matches and match_stats from fixtures
        completed_matches = []
        match_stats = []

        for fixture in fixtures:
            match = await match_repository.read_by_fixture(fixture)
            if match and match.period == PeriodEnum.FULLTIME:
                completed_matches.append(match)
                stats = await match_stat_repository.read_by_match(match)
                if stats:
                    match_stats.extend(stats)

        match_count = len(completed_matches)

        if match_count == 0:
            print(f"  Skipping: No completed matches for season {season.year_start}")
            continue

        print(f"  Found {match_count} completed matches from {len(fixtures)} fixtures")
        print(f"  Found {len(match_stats)} match stats")

        # Calculate analytics values
        # TOTAL_GOALS: Sum of all goals
        total_goals = sum(
            m.home_team_score + m.away_team_score for m in completed_matches
        )

        # PER_MATCH_GOALS: Average goals per match
        per_match_goals = total_goals / match_count if match_count > 0 else 0

        # PER_MATCH_PASS_ACCURACY: Average pass accuracy
        total_pass_accuracy = 0
        pass_accuracy_count = 0
        for stat in match_stats:
            if stat.passes_total > 0:
                accuracy = (stat.passes_accurate / stat.passes_total) * 100
                total_pass_accuracy += accuracy
                pass_accuracy_count += 1
        per_match_pass_accuracy = (
            total_pass_accuracy / pass_accuracy_count if pass_accuracy_count > 0 else 0
        )

        # PER_MATCH_XG: Average expected goals per match
        total_xg = sum(
            stat.expected_goals for stat in match_stats
        )  # 이거 왜 2025/26 다 0이냐
        per_match_xg = total_xg / match_count if match_count > 0 else 0

        # PER_MATCH_SUBSTITUTIONS: Average substitutions per match
        total_substitutions = 0
        for match in completed_matches:
            loaded_match = await match_repository.load_items(match)
            total_substitutions += len(loaded_match.substitution_associations)
        per_match_substitutions = (
            total_substitutions / match_count if match_count > 0 else 0
        )

        # PER_MATCH_YELLOW_CARDS: Average yellow cards per match
        total_yellow_cards = sum(stat.discipline_yellow_cards for stat in match_stats)
        per_match_yellow_cards = (
            total_yellow_cards / match_count if match_count > 0 else 0
        )

        # TOTAL_RED_CARDS: Sum of all red cards
        total_red_cards = sum(stat.discipline_red_cards for stat in match_stats)

        # Store current values for next iteration
        current_values: Dict[AnalyticsKeyEnum, float] = {
            AnalyticsKeyEnum.PER_MATCH_GOALS: per_match_goals,
            AnalyticsKeyEnum.PER_MATCH_PASS_ACCURACY: per_match_pass_accuracy,
            AnalyticsKeyEnum.PER_MATCH_SUBSTITUTIONS: per_match_substitutions,
            AnalyticsKeyEnum.PER_MATCH_XG: per_match_xg,
            AnalyticsKeyEnum.PER_MATCH_YELLOW_CARDS: per_match_yellow_cards,
            AnalyticsKeyEnum.TOTAL_GOALS: float(total_goals),
            AnalyticsKeyEnum.TOTAL_RED_CARDS: float(total_red_cards),
        }

        # Create and upsert analytics entities
        # Format: (key, title_en, title_kr, value, description_en, description_kr)
        analytics_data = [
            (
                AnalyticsKeyEnum.PER_MATCH_GOALS,
                "Goals Per Match",
                "경기당 골",
                per_match_goals,
                "Average goals per match",
                "경기당 평균 골 수",
            ),
            (
                AnalyticsKeyEnum.PER_MATCH_PASS_ACCURACY,
                "Pass Accuracy",
                "패스 정확도",
                per_match_pass_accuracy,
                "Average pass accuracy percentage",
                "평균 패스 정확도 (%)",
            ),
            (
                AnalyticsKeyEnum.PER_MATCH_SUBSTITUTIONS,
                "Substitutions Per Match",
                "경기당 교체",
                per_match_substitutions,
                "Average substitutions per match",
                "경기당 평균 교체 수",
            ),
            (
                AnalyticsKeyEnum.PER_MATCH_XG,
                "xG Per Match",
                "경기당 기대득점",
                per_match_xg,
                "Average expected goals per match",
                "경기당 평균 기대득점(xG)",
            ),
            (
                AnalyticsKeyEnum.PER_MATCH_YELLOW_CARDS,
                "Yellow Cards Per Match",
                "경기당 옐로카드",
                per_match_yellow_cards,
                "Average yellow cards per match",
                "경기당 평균 옐로카드 수",
            ),
            (
                AnalyticsKeyEnum.TOTAL_GOALS,
                "Total Goals",
                "총 득점",
                total_goals,
                "Total goals scored in the season",
                "시즌 총 득점 수",
            ),
            (
                AnalyticsKeyEnum.TOTAL_RED_CARDS,
                "Total Red Cards",
                "총 레드카드",
                total_red_cards,
                "Total red cards in the season",
                "시즌 총 레드카드 수",
            ),
        ]

        for (
            key,
            title_en,
            title_kr,
            value,
            description_en,
            description_kr,
        ) in analytics_data:
            # Calculate delta as percentage change from previous season
            delta = None
            if key in previous_values and previous_values[key] != 0:
                delta = (
                    (float(value) - previous_values[key]) / previous_values[key]
                ) * 100

            analytics_entity = AnalyticsEntity(
                key=key,
                title_en=title_en,
                title_kr=title_kr,
                value=float(value),
                season=season,
                source=SourceEnum.PULSELIVE,
                source_id=f"{season.source_id}_{key.value}",
                delta=delta,
                description_en=description_en,
                description_kr=description_kr,
            )
            result = await analytics_repository.upsert(analytics_entity)
            all_upserted_analytics.append(result)
            delta_str = f" (Δ {delta:+.2f}%)" if delta is not None else ""
            print(f"    ✅ {key.value}: {value:.2f}{delta_str}")

        # Update previous values for next season
        previous_values = current_values.copy()

        print(
            f"  Upserted {len(analytics_data)} analytics for season {season.year_start}"
        )

    print(f"\n{'=' * 80}")
    print(f"Total upserted: {len(all_upserted_analytics)} analytics entities")
    print("=" * 80)

    return all_upserted_analytics


async def update_championship(
    service_container: CommonServiceContainer,
    repository_container: CommonRepositoryContainer,
) -> Dict:
    """
    Update championship associations for completed seasons.

    Identifies completed seasons (date_end has passed), determines winning teams,
    and updates both team and player championship associations. Players must have
    appeared in 5+ matches during the season to qualify.

    :param service_container: Service container for configuration and utilities
    :param repository_container: Repository container for database operations
    :returns: Dictionary with update statistics and processed entities
    """
    print("=" * 80)
    print("Championship Update Process")
    print("=" * 80)

    # Phase 1: Setup & Initialization
    print("\nPhase 1: Initializing services and repositories...")

    competition_repository = repository_container.competition_repository()
    season_repository = repository_container.season_repository()
    team_repository = repository_container.team_repository()
    player_repository = repository_container.player_repository()
    team_stat_repository = repository_container.team_stat_repository()
    match_repository = repository_container.match_repository()

    # Phase 2: Season Analysis
    print("Phase 2: Analyzing completed seasons...")

    # Get target competition (Pulselive ID = 8)
    competition = await competition_repository.read_by_pulselive_id(8)
    if not competition:
        print("Error: Competition not found")
        return {"error": "Competition not found"}

    # Read all seasons for the competition
    seasons = await season_repository.read_by_competition(competition)
    if not seasons:
        print("Warning: No seasons found")
        return {"warning": "No seasons found"}

    # Get current time
    current_time = create_utc_now()

    # Filter completed seasons (date_end has passed)
    completed_seasons = [season for season in seasons if season.date_end < current_time]

    # Sort chronologically
    completed_seasons.sort(key=lambda s: s.year_start)

    print(
        f"Found {len(completed_seasons)} completed seasons out of {len(seasons)} total seasons"
    )

    # Initialize results tracking
    results = {"seasons_processed": [], "summary": {"errors": []}}

    # Phase 3-6: Process each completed season
    for season in completed_seasons:
        print(f"\n{'=' * 40}")
        print(f"Processing Season {season.year_start}")
        print(f"{'=' * 40}")

        season_result = {
            "season": season,
            "year": season.year_start,
            "winner": None,
            "team_updated": False,
            "qualifying_players_count": 0,
            "players_updated_count": 0,
            "players_skipped_count": 0,
        }

        try:
            # Phase 3: Winner Identification
            print("Phase 3: Identifying championship winner...")

            # Get all team stats for season
            team_stats = await team_stat_repository.read_by_season(season)

            if not team_stats:
                print(f"Warning: No team stats found for season {season.year_start}")
                results["summary"]["errors"].append(
                    f"No team stats for season {season.year_start}"
                )
                results["seasons_processed"].append(season_result)
                continue

            # Filter for overall_position 1 (winner)
            winners = [stat for stat in team_stats if stat.overall_position == 1]

            if len(winners) == 0:
                print(f"Warning: No winner found for season {season.year_start}")
                results["summary"]["errors"].append(
                    f"No winner for season {season.year_start}"
                )
                results["seasons_processed"].append(season_result)
                continue

            if len(winners) > 1:
                print(f"Warning: Multiple winners found for season {season.year_start}")
                results["summary"]["errors"].append(
                    f"Multiple winners for season {season.year_start}"
                )
                results["seasons_processed"].append(season_result)
                continue

            # Get team entity from winning team stat
            winner_team = await team_repository.read_by_id(winners[0].team_id)
            if not winner_team:
                print(f"Error: Winner team not found for season {season.year_start}")
                results["summary"]["errors"].append(
                    f"Winner team not found for season {season.year_start}"
                )
                results["seasons_processed"].append(season_result)
                continue

            season_result["winner"] = winner_team
            print(f"Winner identified: {winner_team.name_en}")

            # Phase 4: Team Championship Update
            print("Phase 4: Updating team championship association...")

            try:
                print(
                    f"DEBUG: Calling append_championship_season for {winner_team.name_en}..."
                )
                updated_team = await team_repository.append_championship_season(
                    winner_team, season
                )
                print(f"DEBUG: append_championship_season completed, calling update...")
                await team_repository.update(updated_team)
                print(f"DEBUG: update completed successfully")
                season_result["team_updated"] = True
                print(f"✅ Team championship updated for {winner_team.name_en}")
            except Exception as e:
                print(f"Error updating team championship: {e}")
                import traceback

                traceback.print_exc()
                results["summary"]["errors"].append(
                    f"Team update error for season {season.year_start}: {e}"
                )

            # Phase 5: Qualifying Player Identification
            print("Phase 5: Identifying qualifying players (5+ appearances)...")

            # Get all matches for team in season
            print(
                f"DEBUG: Calling read_by_team_on_season for {winner_team.name_en} in season {season.year_start}..."
            )
            matches = await match_repository.read_by_team_on_season(
                season=season, team=winner_team
            )
            print(
                f"DEBUG: Found {len(matches)} matches for {winner_team.name_en} in season {season.year_start}"
            )

            # Track player appearance counts
            player_appearances = {}

            for idx, match in enumerate(matches):
                # Load match associations (lineups, substitutes)
                loaded_match = await match_repository.load_items(match)

                # Determine if team is home or away
                is_home = loaded_match.home_team_id == winner_team.id

                if idx == 0:  # Log first match details
                    print(
                        f"DEBUG: First match {loaded_match.id} - home_team_id: {loaded_match.home_team_id}, away_team_id: {loaded_match.away_team_id}"
                    )
                    print(
                        f"DEBUG: winner_team.id: {winner_team.id}, is_home: {is_home}"
                    )
                    print(
                        f"DEBUG: lineup_associations count: {len(loaded_match.lineup_associations)}"
                    )
                    print(
                        f"DEBUG: substitution_associations count: {len(loaded_match.substitution_associations)}"
                    )

                # Count lineup appearances
                for lineup_assoc in loaded_match.lineup_associations:
                    if lineup_assoc.is_home == is_home:
                        player_id = lineup_assoc.player_id
                        player_appearances[player_id] = (
                            player_appearances.get(player_id, 0) + 1
                        )

                # Count substitute appearances (only if they actually played)
                for sub_assoc in loaded_match.substitution_associations:
                    if sub_assoc.is_home == is_home:
                        in_player_id = sub_assoc.in_player_id
                        player_appearances[in_player_id] = (
                            player_appearances.get(in_player_id, 0) + 1
                        )

            # Filter players with 5+ appearances
            qualifying_player_ids = [
                player_id
                for player_id, count in player_appearances.items()
                if count >= 5
            ]

            season_result["qualifying_players_count"] = len(qualifying_player_ids)
            print(
                f"Found {len(qualifying_player_ids)} qualifying players for {winner_team.name_en}"
            )

            # Phase 6: Player Championship Update
            print("Phase 6: Updating player championship associations...")

            for player_id in qualifying_player_ids:
                try:
                    player = await player_repository.read_by_id(player_id)
                    if not player:
                        print(f"Warning: Player {player_id} not found")
                        season_result["players_skipped_count"] += 1
                        continue

                    updated_player = await player_repository.append_championship_season(
                        player, season
                    )
                    await player_repository.update(updated_player)
                    season_result["players_updated_count"] += 1

                    if season_result["players_updated_count"] % 5 == 0:
                        print(
                            f"  Updated {season_result['players_updated_count']}/{len(qualifying_player_ids)} players..."
                        )

                except Exception as e:
                    print(f"Error updating player {player_id}: {e}")
                    season_result["players_skipped_count"] += 1
                    results["summary"]["errors"].append(
                        f"Player {player_id} update error: {e}"
                    )

            print(
                f"✅ Updated {season_result['players_updated_count']} players, skipped {season_result['players_skipped_count']}"
            )

        except Exception as e:
            print(f"Error processing season {season.year_start}: {e}")
            results["summary"]["errors"].append(
                f"Season {season.year_start} processing error: {e}"
            )

        results["seasons_processed"].append(season_result)

    # Phase 7: Results & Reporting
    print("\n" + "=" * 80)
    print("Championship Update Summary")
    print("=" * 80)

    total_teams_updated = sum(
        1 for sr in results["seasons_processed"] if sr["team_updated"]
    )
    total_players_updated = sum(
        sr["players_updated_count"] for sr in results["seasons_processed"]
    )
    total_players_processed = sum(
        sr["qualifying_players_count"] for sr in results["seasons_processed"]
    )

    for season_result in results["seasons_processed"]:
        print(f"\nSeason {season_result['year']}:")
        print(
            f"  Winner: {season_result['winner'].name_en if season_result['winner'] else 'N/A'}"
        )
        print(
            f"  Team Championship: {'✅ Updated' if season_result['team_updated'] else '❌ Skipped'}"
        )
        print(f"  Qualifying Players: {season_result['qualifying_players_count']}")
        print(f"  Players Updated: {season_result['players_updated_count']}")
        print(f"  Players Skipped: {season_result['players_skipped_count']}")

    results["summary"]["total_seasons"] = len(results["seasons_processed"])
    results["summary"]["total_teams_updated"] = total_teams_updated
    results["summary"]["total_players_updated"] = total_players_updated
    results["summary"]["total_players_processed"] = total_players_processed

    print("\n" + "=" * 80)
    print(f"Total Seasons Processed: {results['summary']['total_seasons']}")
    print(f"Total Teams Updated: {results['summary']['total_teams_updated']}")
    print(f"Total Players Updated: {results['summary']['total_players_updated']}")
    print(f"Total Errors: {len(results['summary']['errors'])}")
    print("=" * 80)

    return results


async def update_momentum(
    repository_container: CommonRepositoryContainer,
    team_stats: list[TeamStatEntity],
    window_size: int = 5,
    beta: float = 0.5,
) -> list[TeamStatEntity]:
    """
    Calculate and update momentum index for all team stats in a season.

    Implements the Team Momentum Index formula:
    - ΔPPM = PPM(recent N matches) - PPM(season average)
    - ΔxG = average xG difference over N matches
    - Momentum = 100 * tanh(β * (0.6 * z(ΔPPM) + 0.4 * z(ΔxG)))

    :param repository_container: Repository container for database operations
    :param team_stats: List of team stat entities for a single season
    :param window_size: N - number of recent matches to consider (default: 5)
    :param beta: Scaling factor for momentum calculation (default: 0.5)
    :returns: List of updated team stat entities with momentum values
    """
    if not team_stats:
        return []

    match_stat_repository = repository_container.match_stat_repository()
    match_repository = repository_container.match_repository()

    # Step 1: Calculate raw momentum values for each team
    ppm_deltas: list[float | None] = []
    xg_deltas: list[float | None] = []

    for team_stat in team_stats:
        # Calculate season PPM
        if team_stat.overall_matches == 0:
            ppm_deltas.append(None)
            xg_deltas.append(None)
            continue

        ppm_season = team_stat.overall_points / team_stat.overall_matches

        # Calculate recent matches PPM from cumulative points
        cumulative = team_stat.overall_cumulative_points
        total_matches = len(cumulative)

        if total_matches == 0:
            # No matches at all
            ppm_deltas.append(None)
            xg_deltas.append(None)
            continue

        # Use effective window size (min of requested window and available matches)
        effective_window = min(window_size, total_matches)

        # PPM(N) = (C[M] - C[M-N]) / N
        # When M == effective_window, C[M-N] = C[0] = 0
        if total_matches > effective_window:
            points_recent = cumulative[-1] - cumulative[-(effective_window + 1)]
        else:
            # All matches are within the window
            points_recent = cumulative[-1]

        ppm_recent = points_recent / effective_window
        delta_ppm = ppm_recent - ppm_season
        ppm_deltas.append(delta_ppm)

        # Get recent matches for xG calculation (use effective window)
        match_associations = sorted(
            team_stat.match_associations, key=lambda x: x.kickoff_time
        )
        recent_associations = match_associations[-effective_window:]

        xg_diffs = []
        for assoc in recent_associations:
            match = await match_repository.read_by_id(assoc.match_id)
            if not match:
                continue

            match_stats = await match_stat_repository.read_by_match(match)
            if len(match_stats) != 2:
                continue

            # Find team's xG and opponent's xG
            team_xg = None
            opponent_xg = None
            for stat in match_stats:
                if stat.team_id == team_stat.team_id:
                    team_xg = stat.expected_goals
                else:
                    opponent_xg = stat.expected_goals

            if team_xg is not None and opponent_xg is not None:
                xg_diffs.append(team_xg - opponent_xg)

        if xg_diffs:
            delta_xg = sum(xg_diffs) / len(xg_diffs)
            xg_deltas.append(delta_xg)
        else:
            xg_deltas.append(None)

    # Step 2: Calculate z-scores for teams with valid values
    valid_ppm = [v for v in ppm_deltas if v is not None]
    valid_xg = [v for v in xg_deltas if v is not None]

    # Calculate mean and std for z-score normalization
    def calculate_z_scores(
        values: list[float | None], valid_values: list[float]
    ) -> list[float | None]:
        if len(valid_values) < 2:
            return [None] * len(values)

        mean = sum(valid_values) / len(valid_values)
        variance = sum((v - mean) ** 2 for v in valid_values) / len(valid_values)
        std = math.sqrt(variance) if variance > 0 else 1.0

        return [(v - mean) / std if v is not None else None for v in values]

    z_ppm = calculate_z_scores(ppm_deltas, valid_ppm)
    z_xg = calculate_z_scores(xg_deltas, valid_xg)

    # Step 3: Calculate final momentum and update entities
    for i, team_stat in enumerate(team_stats):
        if z_ppm[i] is not None and z_xg[i] is not None:
            # Momentum = 100 * tanh(β * (0.6 * z(ΔPPM) + 0.4 * z(ΔxG)))
            combined_z = 0.6 * z_ppm[i] + 0.4 * z_xg[i]
            team_stat.momentum = 100 * math.tanh(beta * combined_z)
        else:
            # Not enough data for momentum calculation (z-score requires at least 2 teams)
            team_stat.momentum = None

    return team_stats


async def update_player_stats(
    repository_container: CommonRepositoryContainer,
) -> list[PlayerStatEntity]:
    """
    Calculate and update minutes_played for all player stats in each season.

    Calculates total playing time for each player based on:
    - Starting lineup: match.clock (full match) or substitution.clock (if subbed out)
    - Substituted in: match.clock - substitution.clock

    :param repository_container: Repository container for database operations
    :returns: List of updated player stat entities
    """
    print("=" * 80)
    print("Player Stats Update Process (Minutes Played)")
    print("=" * 80)

    # Initialize repositories
    competition_repository = repository_container.competition_repository()
    season_repository = repository_container.season_repository()
    fixture_repository = repository_container.fixture_repository()
    match_repository = repository_container.match_repository()
    player_stat_repository = repository_container.player_stat_repository()

    # Get competition
    competition = await competition_repository.read_by_pulselive_id(8)
    if not competition:
        print("Error: Competition not found")
        return []

    # Get seasons sorted from oldest to newest
    seasons = await season_repository.read_by_competition(competition)
    if not seasons:
        print("Error: No seasons found")
        return []

    seasons.sort(key=lambda s: s.year_start)

    all_updated_player_stats = []

    for season in seasons:
        print(f"\nProcessing season {season.year_start}...")

        # Step 1: Get all completed matches for the season
        fixtures = await fixture_repository.read_by_season(season)
        if not fixtures:
            print(f"  No fixtures found for season {season.year_start}")
            continue

        completed_matches = []
        for fixture in fixtures:
            match = await match_repository.read_by_fixture(fixture)
            if match and match.period == PeriodEnum.FULLTIME:
                loaded_match = await match_repository.load_items(match)
                completed_matches.append(loaded_match)

        if not completed_matches:
            print(f"  No completed matches found for season {season.year_start}")
            continue

        print(f"  Found {len(completed_matches)} completed matches")

        # Step 2: Calculate minutes played for each player
        player_minutes: dict[str, int] = {}  # player_id -> total minutes

        for match in completed_matches:
            match_duration = match.clock or 90  # Default to 90 if clock is None

            # Build substitution lookup: player_id -> substitution clock
            # For players subbed OUT
            subbed_out_at: dict[str, int] = {}
            # For players subbed IN
            subbed_in_at: dict[str, int] = {}

            for sub in match.substitution_associations:
                subbed_out_at[sub.out_player_id] = sub.clock
                subbed_in_at[sub.in_player_id] = sub.clock

            # Calculate minutes for starting lineup players
            for lineup in match.lineup_associations:
                player_id = lineup.player_id

                if player_id in subbed_out_at:
                    # Player was substituted out
                    minutes = subbed_out_at[player_id]
                else:
                    # Player played full match
                    minutes = match_duration

                player_minutes[player_id] = player_minutes.get(player_id, 0) + minutes

            # Calculate minutes for substituted-in players
            for player_id, sub_clock in subbed_in_at.items():
                minutes = match_duration - sub_clock
                player_minutes[player_id] = player_minutes.get(player_id, 0) + minutes

        print(f"  Calculated minutes for {len(player_minutes)} players")

        # Step 3: Update player_stats with minutes_played
        updated_count = 0
        for player_id, total_minutes in player_minutes.items():
            # Find player_stat for this player and season
            player_stat = await player_stat_repository.read_by_player_season_id(
                player_id=player_id, season_id=season.id
            )

            if player_stat:
                player_stat.minutes_played = total_minutes
                await player_stat_repository.update(player_stat)
                all_updated_player_stats.append(player_stat)
                updated_count += 1

        print(f"  Updated {updated_count} player stats for season {season.year_start}")

    print(f"\n{'=' * 80}")
    print(f"Total updated: {len(all_updated_player_stats)} player stat entities")
    print("=" * 80)

    return all_updated_player_stats

    """

⏺ 구현을 완료했습니다. 아래는 각 단계별 설명입니다.

  ---
  update_player_stats 함수 - 단계별 설명

  Step 1: 시즌별 완료된 경기 조회

  fixtures = await fixture_repository.read_by_season(season)
  completed_matches = [match for match if match.period == PeriodEnum.FULLTIME]
  - 해당 시즌의 모든 fixture 조회
  - FULLTIME 상태인 경기만 필터링
  - 각 경기의 lineup_associations, substitution_associations 로드

  Step 2: 선수별 출전 시간 계산

  player_minutes: dict[str, int] = {}  # player_id -> 총 출전 시간

  선발 출전 선수:
  | 상황        | 계산                                 |
  |-------------|--------------------------------------|
  | 풀타임 출전 | match.clock (전체 경기 시간)         |
  | 교체 아웃   | substitution.clock (교체된 시점까지) |

  교체 투입 선수:
  | 상황    | 계산                             |
  |---------|----------------------------------|
  | 교체 인 | match.clock - substitution.clock |

  Step 3: PlayerStat 업데이트

  player_stat = await player_stat_repository.read_by_player_season_id(player_id, season_id)
  player_stat.minutes_played = total_minutes
  await player_stat_repository.update(player_stat)
  - 해당 시즌의 player_stat 조회
  - minutes_played 필드에 총 출전 시간 저장
  - DB 업데이트

  ---
  수정된 파일 요약

  | 파일                      | 변경 내용                                                                          |
  |---------------------------|------------------------------------------------------------------------------------|
  | player_stat_entity.py     | minutes_played = Column(Integer, nullable=True) 필드 추가                          |
  | player_stat_repository.py | read_by_player_season_id() 메서드 추가, upsert_player_stat()에 minutes_played 포함 |
  | b.py                      | update_player_stats() 함수 추가                                                    |
    """


async def reset_team_stats(
    repository_container: CommonRepositoryContainer,
    webclient: PulseliveNewWebclient,
) -> list[TeamStatEntity]:
    """
    Reset and recalculate all team statistics for each season.

    Iterates through seasons from oldest to newest, resets all team_stat values
    using reset_statistics(), then calls pull_team_stats to refresh data from API
    and recreate team_stat_match_associations.

    :param repository_container: Repository container for database operations
    :param webclient: PulseLive webclient for API calls
    :returns: List of updated team stat entities
    """
    print("=" * 80)
    print("Team Stats Reset Process")
    print("=" * 80)

    # Initialize repositories
    competition_repository = repository_container.competition_repository()
    season_repository = repository_container.season_repository()
    team_repository = repository_container.team_repository()
    team_stat_repository = repository_container.team_stat_repository()
    ground_repository = repository_container.ground_repository()

    # Initialize puller
    team_stat_puller = PulseliveNewTeamStatsPuller(repository_container, webclient)

    # Get competition
    competition = await competition_repository.read_by_pulselive_id(8)
    if not competition:
        print("Error: Competition not found")
        return []

    # Get seasons sorted from oldest to newest
    seasons = await season_repository.read_by_competition(competition)
    if not seasons:
        print("Error: No seasons found")
        return []

    seasons.sort(key=lambda s: s.year_start)

    all_updated_team_stats = []

    for season in seasons:
        if season.year_start < 2024:
            continue
        print(f"\nProcessing season {season.year_start}...")

        # Read existing team_stats for season
        team_stats = await team_stat_repository.read_by_season(season)
        if not team_stats:
            print(f"  No team stats found for season {season.year_start}")
            continue

        print(f"  Found {len(team_stats)} team stats")

        # Get teams from API for this season
        teams_response = await webclient.get_v1_teams(
            competition_id=competition.source_id, season_id=season.season_source_id
        )

        season_team_stats = []

        for team_stat in team_stats:
            try:
                # Get team entity
                team = await team_repository.read_by_id(team_stat.team_id)
                if not team:
                    print(f"  Warning: Team not found for team_stat {team_stat.id}")
                    continue

                # Find ground from API response
                ground = None
                for team_data in teams_response.data:
                    if str(team_data.id) == team.source_id:
                        ground = await ground_repository.read_by_name_en(
                            team_data.stadium.name
                        )
                        break

                # Pull fresh data using pull_team_stats with force_reset
                updated_team_stat = await team_stat_puller.pull_team_stats(
                    team, competition, season, ground, force_reset=True
                )

                if updated_team_stat:
                    season_team_stats.append(updated_team_stat)
                    print(f"    ✅ Reset and updated: {team.name_en}")

            except Exception as e:
                print(f"    ❌ Error processing team_stat {team_stat.id}: {e}")
                continue

        # Update positions for all team stats in this season
        if season_team_stats:
            for i, team_stat in enumerate(season_team_stats):
                season_team_stats[i] = await team_stat_repository.update_position(
                    team_stat, season_team_stats
                )

            # Update momentum for all teams in this season
            print(f"  Calculating momentum for {len(season_team_stats)} teams...")
            season_team_stats = await update_momentum(
                repository_container, season_team_stats
            )

            # Save all team stats to database
            for team_stat in season_team_stats:
                await team_stat_repository.update(team_stat)
                all_updated_team_stats.append(team_stat)

            # Print momentum summary
            teams_with_momentum = sum(
                1 for ts in season_team_stats if ts.momentum is not None
            )
            print(f"  Momentum calculated for {teams_with_momentum} teams")

        print(
            f"  Updated {len(season_team_stats)} team stats for season {season.year_start}"
        )

    print(f"\n{'=' * 80}")
    print(f"Total updated: {len(all_updated_team_stats)} team stat entities")
    print("=" * 80)

    return all_updated_team_stats


async def update_team_positions(
    repository_container: CommonRepositoryContainer,
) -> list[TeamStatEntity]:
    """
    Update position values for all team stats in each season.

    Reads existing team_stats, recalculates positions using update_position,
    and saves the updated entities to the database.

    :param repository_container: Repository container for database operations
    :returns: List of updated team stat entities
    """
    print("=" * 80)
    print("Team Positions Update Process")
    print("=" * 80)

    # Initialize repositories
    competition_repository = repository_container.competition_repository()
    season_repository = repository_container.season_repository()
    team_stat_repository = repository_container.team_stat_repository()

    # Get competition
    competition = await competition_repository.read_by_pulselive_id(8)
    if not competition:
        print("Error: Competition not found")
        return []

    # Get seasons sorted from oldest to newest
    seasons = await season_repository.read_by_competition(competition)
    if not seasons:
        print("Error: No seasons found")
        return []

    seasons.sort(key=lambda s: s.year_start)

    all_updated_team_stats = []

    for season in seasons:
        if season.year_start < 2024:
            continue
        print(f"\nProcessing season {season.year_start}...")

        # Read existing team_stats for season
        team_stats = await team_stat_repository.read_by_season(season)
        if not team_stats:
            print(f"  No team stats found for season {season.year_start}")
            continue

        print(f"  Found {len(team_stats)} team stats")

        # Update positions for all team stats using index to preserve updates
        for i, team_stat in enumerate(team_stats):
            team_stats[i] = await team_stat_repository.update_position(
                team_stat, team_stats
            )
            print(
                f"    ✅ {team_stats[i].team_id}: position {team_stats[i].overall_position}"
            )

        # Save all team stats to database
        for team_stat in team_stats:
            await team_stat_repository.update(team_stat)
            all_updated_team_stats.append(team_stat)

        print(
            f"  Updated {len(team_stats)} team positions for season {season.year_start}"
        )

    print(f"\n{'=' * 80}")
    print(f"Total updated: {len(all_updated_team_stats)} team stat entities")
    print("=" * 80)

    return all_updated_team_stats


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
    # await create_match(
    #     service_container,
    #     repository_container,
    #     webclient_service,
    # )
    await update_match(
        service_container,
        repository_container,
        webclient_service,
    )
    # await create_award(
    #     service_container,
    #     repository_container,
    #     webclient_service,
    # )
    # await create_news(config_service, db_service)
    # await update_championship(service_container, repository_container)
    # await update_match(service_container, repository_container, webclient_service)
    # await reset_team_stats(repository_container, webclient_service)
    # await update_team_positions(repository_container)
    # await upsert_analytics(repository_container, db_service)
    # await update_player_stats(repository_container)


run(runrun())
