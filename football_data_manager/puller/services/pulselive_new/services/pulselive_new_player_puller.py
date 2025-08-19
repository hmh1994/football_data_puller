from typing import Dict

from httpx import HTTPStatusError

from football_data_manager.common.enums.position_enum import PositionEnum
from football_data_manager.common.enums.side_enum import SideEnum
from football_data_manager.common.repositories.competitions.competition_entity import (
    CompetitionEntity,
)
from football_data_manager.common.repositories.players.player_entity import (
    PlayerEntity,
)
from football_data_manager.common.repositories.players.player_repository import (
    PlayerRepository,
)
from football_data_manager.common.repositories.repository_container import (
    CommonRepositoryContainer,
)
from football_data_manager.common.repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.repositories.teams.team_entity import TeamEntity
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
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_v2_squad_response import (
    PulseliveNewPlayerDetailResponse,
)


class PulseliveNewPlayerPuller:
    """
    Service for pulling player data from PulseLive v2 squad API.

    Handles fetching player squad information for specific teams and persisting
    player data to the database. Processes player names, positions, birth countries
    with proper translation and entity creation.

    :ivar __player_repository: Repository for player database operations
    :ivar __webclient: HTTP client for PulseLive API requests
    :ivar __translator: Translation service for Korean names and countries
    :ivar __country_translation_cache: Cache for country translations to avoid repeated calls
    :ivar __resource_client: Resource validation client for photo URLs
    """

    __player_repository: PlayerRepository
    __repository_container: CommonRepositoryContainer
    __webclient: PulseliveNewWebclient
    __translator: TranslatorService
    __country_translation_cache: Dict[str, str]
    __resource_client: ResourceValidationClient

    def __init__(
        self,
        repository_container: CommonRepositoryContainer,
        pulselive_service: PulseliveNewWebclient,
        service_container: CommonServiceContainer,
    ):
        """
        Initialize the player puller.

        :param repository_container: Container with repository instances
        :param pulselive_service: HTTP client for PulseLive API
        :param service_container: Container with common services including translator
        """
        self.__repository_container = repository_container
        self.__player_repository = repository_container.player_repository()
        self.__webclient = pulselive_service
        self.__translator = service_container.translator_service()
        self.__country_translation_cache = {}
        self.__resource_client = ResourceValidationClient()

    async def pull_players_for_team(
        self,
        competition: CompetitionEntity,
        season: SeasonEntity,
        team: TeamEntity,
    ) -> list[PlayerEntity]:
        """
        Pull all players for a specific team from the PulseLive v2 squad API.

        Retrieves player information including personal details, positions,
        and physical attributes for the given team, processes them with
        translation, and stores in the database.

        :param competition: Competition entity
        :param season: Season entity
        :param team: Team entity to pull players for
        :returns: List of player entities created or updated
        """
        if competition.id != season.competition_id:
            raise ValueError(
                f"Season {season.id} does not belong to competition {competition.id}"
            )

        # Get squad data from API
        try:
            squad_response = await self.__webclient.get_v2_squad(
                competition.source_id, season.season_source_id, team.source_id
            )
        except HTTPStatusError:
            return []

        # Process players
        players = await self.__process_players(squad_response.players)

        # Close resource validation client
        await self.__resource_client.close()
        return players

    async def __process_players(
        self, player_items: list[PulseliveNewPlayerDetailResponse]
    ) -> list[PlayerEntity]:
        """
        Process player items from API response into database entities.

        Converts API response objects to player entities with proper
        name localization, country translation, and deduplication,
        then persists them to the database.

        :param player_items: List of player items from API response
        :returns: List of processed player entities
        """
        players = []

        for item in player_items:
            # Process player
            player = await self.__process_player(item)
            if player is not None:
                players.append(player)

        return players

    async def __process_player(
        self, player_item: PulseliveNewPlayerDetailResponse
    ) -> PlayerEntity | None:
        """
        Process player information from API response.

        Creates or retrieves player entity based on player information provided
        in the API response. Handles name localization, country translation,
        and physical attribute data.

        :param player_item: Player response item containing player information
        :returns: Player entity created or retrieved, or None if already exists
        """
        # Check if player already exists
        existing_player = await self.__player_repository.read_by_pulselive_id(
            source_id=player_item.id.player_id
        )

        if existing_player is not None:
            # Check if existing player needs photo URL update
            if not existing_player.photo_url or existing_player.photo_url.strip() == "":
                # Validate Premier League player photo URL
                photo_url = await self.__validate_player_photo(player_item.id.player_id)

                if photo_url:
                    # Update the player's photo URL
                    existing_player.photo_url = photo_url
                    # Save the updated player
                    existing_player = await self.__player_repository.update(
                        existing_player
                    )

            return existing_player

        # Convert position and preferred foot
        position = PositionEnum.from_string(player_item.position)
        if position == PositionEnum.UNKNOWN:
            print(
                f"Unknown position '{player_item.position}' for player '{player_item.name.simple_name}'"
            )
            input("Press Enter to continue...")
        preferred_foot = SideEnum.from_string(player_item.preferred_foot)
        if preferred_foot == SideEnum.UNKNOWN:
            print(
                f"Unknown preferred foot '{player_item.preferred_foot}' for player '{player_item.name.simple_name}'"
            )

        # Create new player entity
        player = PlayerEntity(
            birth_country=player_item.country_of_birth,
            birth_date=player_item.dates.birth,
            display_name_en=player_item.name.simple_name,
            display_name_kr=await self.__translator.translate_word(
                player_item.name.simple_name
            ),
            full_name=player_item.name.full_name,
            nationality_en=player_item.country.country,
            nationality_kr=await self.__get_translated_country(
                player_item.country.country
            ),
            nationality_flag_icon_url=await self.__validate_player_nationality_flag_icon_url(
                player_item.country.iso_code
            ),
            position=position,
            preferred_foot=preferred_foot,
            source_id=player_item.id.player_id,
            height=player_item.height,
            weight=player_item.weight,
            photo_url=await self.__validate_player_photo(player_item.id.player_id),
        )

        return await self.__player_repository.create(player)

    async def __get_translated_country(self, country_en: str) -> str:
        """
        Get translated country name with caching.

        Checks if the country translation already exists in cache or database,
        otherwise translates and caches the result.

        :param country_en: Country name in English
        :returns: Country name in Korean
        """
        # Check memory cache first
        if country_en in self.__country_translation_cache:
            return self.__country_translation_cache[country_en]

        # Check if we have existing translation in database
        existing_translation = await self.__player_repository.get_nationality_kr(
            country_en
        )

        if existing_translation:
            # Cache the existing translation
            self.__country_translation_cache[country_en] = existing_translation
            return existing_translation

        # Translate and cache
        translated_country = await self.__translator.translate_word(country_en)
        self.__country_translation_cache[country_en] = translated_country
        return translated_country

    async def __validate_player_nationality_flag_icon_url(
        self, iso_code: str | None
    ) -> str | None:
        """
        Validate Premier League country flag icon URL and return if it exists.

        Checks if the Premier League country flag icon PNG exists for the given ISO code.
        Returns the URL if it exists, None otherwise.

        :param iso_code: ISO code of the country
        :returns: Flag icon URL if it exists, None otherwise
        """
        if not iso_code:
            return None

        flag_icon_url = (
            f"https://resources.premierleague.com/premierleague/flags/{iso_code}.png"
        )

        if await self.__resource_client.validate_url_exists(flag_icon_url):
            return flag_icon_url

        return None

    async def __validate_player_photo(self, player_id: str) -> str | None:
        """
        Validate Premier League player photo URL and return if it exists.

        Checks if the Premier League player photo PNG exists for the given player ID.
        Returns the URL if it exists, None otherwise.

        :param player_id: Player identifier from the source system
        :returns: Photo URL if it exists, None otherwise
        """
        photo_url = f"https://resources.premierleague.com/premierleague25/photos/players/110x140/{player_id}.png"

        if await self.__resource_client.validate_url_exists(photo_url):
            return photo_url

        return None
