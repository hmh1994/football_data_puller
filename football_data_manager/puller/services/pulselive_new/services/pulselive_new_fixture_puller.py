from football_data_manager.common.repositories.competitions.competition_entity import (
    CompetitionEntity,
)
from football_data_manager.common.repositories.fixtures.fixture_entity import (
    FixtureEntity,
)
from football_data_manager.common.repositories.fixtures.fixture_repository import (
    FixtureRepository,
)
from football_data_manager.common.repositories.grounds.ground_entity import GroundEntity
from football_data_manager.common.repositories.grounds.ground_repository import (
    GroundRepository,
)
from football_data_manager.common.repositories.repository_container import (
    CommonRepositoryContainer,
)
from football_data_manager.common.repositories.seasons.season_entity import SeasonEntity
from football_data_manager.common.repositories.teams.team_repository import (
    TeamRepository,
)
from football_data_manager.common.utils.type_helper.datetime_helper import (
    create_utc_from_string,
)
from football_data_manager.puller.services.pulselive_new.components.pulselive_new_webclient import (
    PulseliveNewWebclient,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_match_response import (
    PulseliveNewMatchResponse,
)


class PulseliveNewFixturePuller:
    """
    Puller service for collecting fixture entities from PulseLive API matchweek endpoints.

    Processes matches from PulseLive's v1 matchweek matches API and creates fixture entities
    with proper team, season, and ground associations. Handles team and ground lookup,
    datetime parsing, and deduplication based on source IDs.

    :ivar __fixture_repository: Repository for fixture entity operations
    :ivar __team_repository: Repository for team entity operations
    :ivar __ground_repository: Repository for ground entity operations
    :ivar __webclient: PulseLive web client for API calls
    """

    __fixture_repository: FixtureRepository
    __team_repository: TeamRepository
    __ground_repository: GroundRepository
    __webclient: PulseliveNewWebclient

    def __init__(
        self,
        repository_container: CommonRepositoryContainer,
        pulselive_service: PulseliveNewWebclient,
    ):
        """
        Initialize the fixture puller.

        :param repository_container: Repository container with entity repositories
        :param pulselive_service: PulseLive web client for API operations
        """
        self.__fixture_repository = repository_container.fixture_repository()
        self.__team_repository = repository_container.team_repository()
        self.__ground_repository = repository_container.ground_repository()
        self.__webclient = pulselive_service

    async def pull_fixtures(
        self,
        competition: CompetitionEntity,
        season: SeasonEntity,
        matchweek_number: int,
    ) -> list[FixtureEntity]:
        """
        Pull fixtures from PulseLive API for a specific matchweek.

        Fetches all matches for the specified competition season and matchweek,
        processes each match into a fixture entity with proper associations,
        and stores them in the database with deduplication.

        :param competition: Competition entity for the fixtures
        :param season: Season entity for the fixtures
        :param matchweek_number: Matchweek number to fetch fixtures for
        :returns: List of fixture entities
        :raises ValueError: If season lookup fails or required data is missing
        """
        if competition.id != season.competition_id:
            raise ValueError(
                f"Season {season.id} does not belong to competition {competition.id}"
            )

        # Fetch matches from PulseLive API
        matches_response = await self.__webclient.get_v1_matchweek_matches(
            competition_id=competition.source_id,
            season_id=season.season_source_id,
            matchweek_number=matchweek_number,
        )

        # Process each match into a fixture entity
        fixtures = []
        for match in matches_response.data:
            fixture = await self.__process_match(match, season, matchweek_number)
            fixtures.append(fixture)
        fixtures: list[FixtureEntity] = [f for f in fixtures if f is not None]
        await self.__fixture_repository.create_all(fixtures)

        return fixtures

    async def __process_match(
        self,
        match: PulseliveNewMatchResponse,
        season: SeasonEntity,
        matchweek_number: int,
    ) -> FixtureEntity | None:
        """
        Process a single match response into a fixture entity.

        Converts PulseLive match data into a fixture entity with proper team
        and ground associations. Handles team lookup, datetime parsing,
        and ground association where available.

        :param match: PulseLive match response data
        :param season: Season entity for the fixture
        :param matchweek_number: Game week number for the fixture
        :returns: Fixture entity or None if processing fails
        :raises ValueError: If required teams are not found
        """
        fixture = await self.__fixture_repository.read_by_pulselive_id(match.match_id)
        if fixture is not None:
            # If fixture already exists, return it without processing
            return fixture

        # Lookup home and away teams
        home_team = await self.__team_repository.read_by_pulselive_id(
            match.home_team.id
        )
        away_team = await self.__team_repository.read_by_pulselive_id(
            match.away_team.id
        )
        ground = await self.__get_ground(match.ground) if match.ground else None

        if home_team is None:
            raise ValueError(
                f"Home team not found with source_id: {match.home_team.id}"
            )
        if away_team is None:
            raise ValueError(
                f"Away team not found with source_id: {match.away_team.id}"
            )

        # Parse kickoff datetime with timezone
        try:
            kickoff_time = create_utc_from_string(match.kickoff, match.kickoff_timezone)
        except (ValueError, AttributeError) as e:
            raise ValueError(
                f"Failed to parse kickoff time '{match.kickoff}' with timezone '{match.kickoff_timezone}': {e}"
            )

        # Create fixture entity
        fixture = FixtureEntity(
            away_team=away_team,
            game_week=matchweek_number,
            home_team=home_team,
            kickoff_time=kickoff_time,
            season=season,
            source_id=match.match_id,
            ground=ground,
        )

        return fixture

    async def __get_ground(self, ground_name: str) -> GroundEntity | None:
        """
        Get ground entity by name.

        Extracts the first part of ground name (before comma) and attempts to find
        an existing ground entity using the repository's read_by_name_en method.
        Returns None if ground is not found.

        :param ground_name: Name of the ground/venue (may contain comma-separated parts)
        :returns: Ground entity if found, None otherwise
        """
        # Extract the first part before comma for ground name lookup
        ground_search_name = ground_name.split(",")[0].strip()
        return await self.__ground_repository.read_by_name_en(ground_search_name)
