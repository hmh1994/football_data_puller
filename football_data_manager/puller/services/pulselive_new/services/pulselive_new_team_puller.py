from football_data_manager.common.repositories.competitions.competition_entity import (
    CompetitionEntity,
)
from football_data_manager.common.repositories.grounds.ground_entity import (
    GroundEntity,
)
from football_data_manager.common.repositories.grounds.ground_repository import (
    GroundRepository,
)
from football_data_manager.common.repositories.repository_container import (
    CommonRepositoryContainer,
)
from football_data_manager.common.repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.repositories.teams.team_entity import TeamEntity
from football_data_manager.common.repositories.teams.team_repository import (
    TeamRepository,
)
from football_data_manager.common.services.client.resource_validation_client import (
    ResourceValidationClient,
)
from football_data_manager.common.services.common_service_container import (
    CommonServiceContainer,
)
from football_data_manager.common.services.translator.translatorService import (
    TranslatorService,
)
from football_data_manager.puller.services.pulselive_new.components.pulselive_new_webclient import (
    PulseliveNewWebclient,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_v1_teams_response import (
    PulseliveNewTeamResponse,
)


class PulseliveNewTeamPuller:
    """
    Service for pulling team and ground data from PulseLive v1 teams API.

    Handles fetching team information for a specific competition season and persisting
    both team and ground (stadium) data to the database. Processes team names, abbreviations,
    and stadium information with proper entity creation and deduplication.

    :ivar __team_repository: Repository for team database operations
    :ivar __ground_repository: Repository for ground database operations
    :ivar __webclient: HTTP client for PulseLive API requests
    :ivar __translator: Translation service for Korean names
    :ivar __resource_client: Resource validation client for icon URLs
    """

    __team_repository: TeamRepository
    __ground_repository: GroundRepository
    __repository_container: CommonRepositoryContainer
    __webclient: PulseliveNewWebclient
    __translator: TranslatorService
    __resource_client: ResourceValidationClient

    def __init__(
        self,
        repository_container: CommonRepositoryContainer,
        pulselive_service: PulseliveNewWebclient,
        service_container: CommonServiceContainer,
    ):
        """
        Initialize the team puller.

        :param repository_container: Container with repository instances
        :param pulselive_service: HTTP client for PulseLive API
        :param service_container: Container with common services including translator
        """
        self.__repository_container = repository_container
        self.__team_repository = repository_container.team_repository()
        self.__ground_repository = repository_container.ground_repository()
        self.__webclient = pulselive_service
        self.__translator = service_container.translator_service()
        self.__resource_client = ResourceValidationClient()

    async def pull_teams_for_season(
        self, competition: CompetitionEntity, season: SeasonEntity
    ) -> tuple[list[TeamEntity], list[GroundEntity]]:
        """
        Pull all teams and grounds for a specific season from the PulseLive API.

        Retrieves team information including stadium details for the given season,
        processes them, and stores both teams and grounds in the database.

        :param competition: Competition entity to pull teams for
        :param season: Season entity to pull teams for
        :returns: Tuple of (list of team entities, list of ground entities) created or updated
        """
        if season.competition_id != competition.id:
            return [], []

        # Get all teams for the season using pagination
        all_teams = await self.__get_all_teams_for_season(
            competition.source_id, season.season_source_id
        )

        # Process teams and grounds
        teams, grounds = await self.__process_teams_and_grounds(all_teams)

        # Close resource validation client
        await self.__resource_client.close()
        return teams, grounds

    async def __get_all_teams_for_season(
        self, competition_id: str, season_id: str
    ) -> list[PulseliveNewTeamResponse]:
        """
        Get all teams for a specific season using pagination.

        :param competition_id: Competition identifier
        :param season_id: Season identifier
        :returns: List of all teams in the season
        """
        all_teams = []
        _next = None

        while True:
            response = await self.__webclient.get_v1_teams(
                competition_id, season_id, limit=50, _next=_next
            )

            all_teams.extend(response.data)

            if response.pagination.next is None:
                break

            _next = response.pagination.next

        return all_teams

    async def __process_teams_and_grounds(
        self, team_items: list[PulseliveNewTeamResponse]
    ) -> tuple[list[TeamEntity], list[GroundEntity]]:
        """
        Process team items from API response into database entities.

        Converts API response objects to team and ground entities with proper
        name localization and deduplication, then persists them to the database.

        :param team_items: List of team items from API response
        :returns: Tuple of (list of processed team entities, list of processed ground entities)
        """
        teams = []
        grounds = []

        for item in team_items:
            try:
                # Process ground first (teams reference grounds)
                ground = await self.__process_ground(item)
                if ground is not None:
                    grounds.append(ground)

                # Process team
                team = await self.__process_team(item)
                if team is not None:
                    teams.append(team)

            except Exception as error:
                print(f"Error processing team '{item.name}': {error}")

        return teams, grounds

    async def __process_ground(
        self, team_item: PulseliveNewTeamResponse
    ) -> GroundEntity | None:
        """
        Process ground (stadium) information from team API response.

        Creates or retrieves ground entity based on stadium information provided
        in the team response. Handles name localization and capacity data.

        :param team_item: Team response item containing stadium information
        :returns: Ground entity created or retrieved, or None if already exists
        """
        stadium = team_item.stadium

        if stadium.name is None:
            return None

        # Check if ground already exists
        existing_ground = await self.__ground_repository.read_by_pulselive_id(
            source_id=GroundEntity.get_source_id(stadium.name)
        )

        if existing_ground is not None:
            return existing_ground

        ground = GroundEntity(
            city_name_en=stadium.city,
            city_name_kr=await self.__translator.translate_word(stadium.city),
            name_en=stadium.name,
            name_kr=await self.__translator.translate_word(stadium.name),
            capacity=stadium.capacity,
        )

        return await self.__ground_repository.create(ground)

    async def __process_team(
        self, team_item: PulseliveNewTeamResponse
    ) -> TeamEntity | None:
        """
        Process team information from API response.

        Creates or retrieves team entity based on team information provided
        in the API response. Handles name localization and abbreviation data.

        :param team_item: Team response item containing team information
        :returns: Team entity created or retrieved, or None if already exists
        """
        # Check if team already exists
        existing_team = await self.__team_repository.read_by_pulselive_id(
            source_id=team_item.id
        )

        if existing_team is not None:
            # Check if existing team needs icon URL update
            if not existing_team.icon_url or existing_team.icon_url.strip() == "":
                # Validate Premier League badge URL
                icon_url = await self.__validate_team_icon_url(team_item.id)

                if icon_url:
                    # Update the team's icon URL
                    existing_team.icon_url = icon_url
                    # Save the updated team
                    existing_team = await self.__team_repository.update(existing_team)

            return existing_team

        # Create new team entity with translated Korean names
        short_name = team_item.short_name if team_item.short_name else team_item.name

        # Validate Premier League badge URL
        icon_url = await self.__validate_team_icon_url(team_item.id)

        team = TeamEntity(
            abbreviation=team_item.abbr,
            name_en=team_item.name,
            name_kr=await self.__translator.translate_word(team_item.name),
            short_name_en=short_name,
            short_name_kr=await self.__translator.translate_word(short_name),
            source_id=team_item.id,
            icon_url=icon_url,
        )

        # Save to database
        created_team = await self.__team_repository.create(team)
        return created_team

    async def __validate_team_icon_url(self, team_id: str) -> str | None:
        """
        Validate and retrieve the Premier League badge URL for a team.

        Checks if the team has a valid icon URL, otherwise returns None.

        :param team_id: Team identifier to validate badge URL
        :returns: Validated icon URL or None if not available
        """
        badge_url = f"https://resources.premierleague.com/premierleague25/badges-alt/{team_id}.svg"
        if await self.__resource_client.validate_url_exists(badge_url):
            return badge_url

        return None
