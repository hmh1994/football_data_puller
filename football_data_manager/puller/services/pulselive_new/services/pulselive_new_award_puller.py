from datetime import datetime

from httpx import HTTPStatusError

from football_data_manager.common.enums.award_type_enum import AwardTypeEnum
from football_data_manager.common.repositories.awards.award_entity import AwardEntity
from football_data_manager.common.repositories.awards.award_repository import (
    AwardRepository,
)
from football_data_manager.common.repositories.competitions.competition_entity import (
    CompetitionEntity,
)
from football_data_manager.common.repositories.player_stats.player_stat_entity import (
    PlayerStatEntity,
)
from football_data_manager.common.repositories.player_stats.player_stat_repository import (
    PlayerStatRepository,
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
from football_data_manager.common.repositories.staffs.staff_entity import StaffEntity
from football_data_manager.common.repositories.staffs.staff_repository import (
    StaffRepository,
)
from football_data_manager.common.services.common_service_container import (
    CommonServiceContainer,
)
from football_data_manager.common.services.translator.translatorService import (
    TranslatorService,
)
from football_data_manager.common.utils.type_helper.datetime_helper import (
    create_utc_datetime,
)
from football_data_manager.puller.services.pulselive_new.components.pulselive_new_webclient import (
    PulseliveNewWebclient,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_manager_award_response import (
    PulseliveNewManagerAwardResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_player_award_response import (
    PulseliveNewPlayerAwardResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_v1_award_response import (
    PulseliveNewV1AwardResponse,
)


class PulseliveNewAwardPuller:
    """
    Service for pulling award data from PulseLive v1 awards API.

    Handles fetching award information for specific competition seasons and persisting
    award types with player stat and staff award associations to the database.
    Uses AwardTypeEnum for standardized award type classification.

    :ivar __award_repository: Repository for award database operations
    :ivar __player_repository: Repository for player database operations
    :ivar __player_stat_repository: Repository for player stat database operations
    :ivar __staff_repository: Repository for staff database operations
    :ivar __webclient: HTTP client for PulseLive API requests
    :ivar __translator: Translation service for staff name localization
    """

    __award_repository: AwardRepository
    __player_repository: PlayerRepository
    __player_stat_repository: PlayerStatRepository
    __staff_repository: StaffRepository
    __webclient: PulseliveNewWebclient
    __translator: TranslatorService

    def __init__(
        self,
        repository_container: CommonRepositoryContainer,
        pulselive_service: PulseliveNewWebclient,
        service_container: CommonServiceContainer,
    ):
        """
        Initialize the award puller.

        :param repository_container: Container with repository instances
        :param pulselive_service: HTTP client for PulseLive API
        :param service_container: Container with common services including translator
        """
        self.__award_repository = repository_container.award_repository()
        self.__player_repository = repository_container.player_repository()
        self.__player_stat_repository = repository_container.player_stat_repository()
        self.__staff_repository = repository_container.staff_repository()
        self.__webclient = pulselive_service
        self.__translator = service_container.translator_service()

    async def pull_awards_for_season(
        self, competition: CompetitionEntity, season: SeasonEntity
    ) -> tuple[list[AwardEntity], list[PlayerStatEntity], list[StaffEntity]]:
        """
        Pull all awards for a specific season from the PulseLive API.

        Retrieves award information including staff and player awards for the given season,
        processes them, and returns entities with associations appended.

        :param competition: Competition entity to pull awards for
        :param season: Season entity to pull awards for
        :returns: Tuple of (award entities, player stat entities with awards, staff entities with awards)
        :raises ValueError: If season does not belong to competition
        """
        if season.competition_id != competition.id:
            raise ValueError(
                f"Season {season.id} does not belong to competition {competition.id}"
            )

        # Get awards data from API
        try:
            awards_response = await self.__webclient.get_v1_awards(
                competition.source_id, season.season_source_id
            )
        except HTTPStatusError as e:
            print(f"Error fetching awards: {e}")
            return [], [], []

        # Process awards and return entities with associations
        awards, player_stats, staffs = await self.__process_awards(
            awards_response, season
        )

        return awards, player_stats, staffs

    async def __process_awards(
        self,
        awards_response: PulseliveNewV1AwardResponse,
        season: SeasonEntity,
    ) -> tuple[list[AwardEntity], list[PlayerStatEntity], list[StaffEntity]]:
        """
        Process awards from API response into database entities with associations.

        Converts API response objects to award entities and appends associations
        to player stat and staff entities with proper name localization.
        Uses dictionaries to track already-updated entities to prevent overwriting.

        :param awards_response: Award response from API
        :param season: Season entity for context
        :returns: Tuple of (award entities, player stat entities with awards, staff entities with awards)
        """
        award_entities = []

        # Track updated entities by their ID to reuse instances
        player_stat_dict = {}  # player_stat_id -> updated PlayerStatEntity
        staff_dict = {}  # staff_id -> updated StaffEntity

        # Process player awards
        for player_award in awards_response.player_awards:
            # 1. Create/get award type entity
            award = await self.__process_award_type(player_award.type)
            if award:
                award_entities.append(award)

            # 2. Get player stat for the player
            player_stat = await self.__get_player_stat(player_award, season)

            # 3. Append award association to player stat
            if award and player_stat:
                # Use already-updated instance if it exists
                if player_stat.id in player_stat_dict:
                    player_stat = player_stat_dict[player_stat.id]

                updated_player_stat = await self.__append_player_stat_award(
                    player_stat, award, player_award.date
                )
                if updated_player_stat:
                    player_stat_dict[updated_player_stat.id] = updated_player_stat

        # Process staff/manager awards
        for manager_award in awards_response.manager_awards:
            # 1. Create/get award type entity
            award = await self.__process_award_type(manager_award.type)
            if award:
                award_entities.append(award)

            # 2. Get or create staff entity
            staff = await self.__get_or_create_staff(manager_award)

            # 3. Append award association to staff
            if award and staff:
                # Use already-updated instance if it exists
                if staff.id in staff_dict:
                    staff = staff_dict[staff.id]

                updated_staff = await self.__append_staff_award(
                    staff, award, manager_award.date
                )
                if updated_staff:
                    staff_dict[updated_staff.id] = updated_staff

        # Convert dictionaries to lists for return
        player_stat_entities = list(player_stat_dict.values())
        staff_entities = list(staff_dict.values())

        return award_entities, player_stat_entities, staff_entities

    async def __get_player_stat(
        self,
        player_award: PulseliveNewPlayerAwardResponse,
        season: SeasonEntity,
    ) -> PlayerStatEntity | None:
        """
        Get player stat entity for the player in the specific season.

        :param player_award: Player award response containing player information
        :param season: Season entity for context
        :returns: Player stat entity or None if not found
        """
        # First get the player entity by source_id
        player = await self.__player_repository.read_by_pulselive_id(player_award.id)

        if player is None:
            print(
                f"Warning: Player {player_award.name.simple_name} "
                f"(ID: {player_award.id}) not found. "
                f"Run player puller first."
            )
            return None

        # Get player stat by player entity and season entity
        player_stat = await self.__player_stat_repository.read_by_player_season(
            player=player,
            season=season,
        )

        if player_stat is None:
            print(
                f"Warning: PlayerStat for {player_award.name.simple_name} "
                f"(ID: {player_award.id}) in {season.abbreviation} not found. "
                f"Run player stats puller first."
            )

        return player_stat

    async def __get_or_create_staff(
        self, manager_award: PulseliveNewManagerAwardResponse
    ) -> StaffEntity | None:
        """
        Get existing staff or create new staff entity from manager award response.

        :param manager_award: Manager award response containing staff information
        :returns: Staff entity or None if creation fails
        """
        # Try to get existing staff by source_id
        existing_staff = await self.__staff_repository.read_by_pulselive_id(
            source_id=manager_award.id
        )

        if existing_staff is not None:
            return existing_staff

        # Create new staff entity with translation
        staff = StaffEntity(
            display_name_en=manager_award.name.simple_name,
            display_name_kr=await self.__translator.translate_word(
                manager_award.name.simple_name
            ),
            full_name=manager_award.name.full_name,
            source_id=manager_award.id,
        )

        return await self.__staff_repository.create(staff)

    async def __process_award_type(self, award_type_str: str) -> AwardEntity | None:
        """
        Process award type by retrieving existing or creating new award entity.

        Prioritizes using existing awards from repository to maintain referential integrity.
        Creates awards with only type enum, leaving names as null for later manual entry.
        The source_id is auto-generated from the award type.

        :param award_type_str: Award type string from API (e.g., "POTM", "GOTM", "SOTM", "MOTM", "MOTS")
        :returns: Award entity from repository or newly created, or None if processing fails
        """
        # Map award type string to enum
        try:
            award_type_enum = AwardTypeEnum.from_string(award_type_str)
        except ValueError as e:
            print(f"Warning: Unknown award type '{award_type_str}': {e}")
            return None

        # Check if award already exists using auto-generated source_id
        source_id = AwardEntity.get_source_id(award_type_enum)
        existing_award = await self.__award_repository.read_by_pulselive_id(source_id)
        if existing_award is not None:
            return existing_award

        # Create new award entity with only type (source_id auto-generated)
        award = AwardEntity(_type=award_type_enum)

        created_award = await self.__award_repository.create(award)

        # If creation returned None (duplicate), try to read again
        if created_award is None:
            return await self.__award_repository.read_by_pulselive_id(source_id)

        return created_award

    @staticmethod
    def __parse_award_date(date_str: str) -> datetime | None:
        """
        Parse award date string from PulseLive API format to datetime.

        :param date_str: Date string in format "YYYY-M" (e.g., "2024-9")
        :returns: Datetime object set to first day of the month, or None if parsing fails
        """
        try:
            parts = list(map(int, date_str.split("-")))

            year = parts[0]
            month = parts[1] if len(parts) > 1 else 1
            day = parts[2] if len(parts) > 2 else 1

            return create_utc_datetime(year, month, day)
        except ValueError as e:
            print(f"Error parsing date {date_str}: {e}")
            return None

    async def __append_player_stat_award(
        self,
        player_stat: PlayerStatEntity,
        award: AwardEntity,
        date_str: str,
    ) -> PlayerStatEntity | None:
        """
        Append award association to player stat entity.

        Uses PlayerStatRepository's append_award_association method to maintain
        proper entity relationship management patterns.

        :param player_stat: Player stat entity receiving the award
        :param award: Award entity being given
        :param date_str: Date string in format "YYYY-M" or "YYYY-M-D"
        :returns: Updated player stat entity with award appended, or None if date parsing fails
        """
        # Parse date using utility function
        award_date = self.__parse_award_date(date_str)
        if award_date is None:
            return None

        # Append association using repository method
        return await self.__player_stat_repository.append_award_association(
            player_stat=player_stat, award=award, date=award_date
        )

    async def __append_staff_award(
        self,
        staff: StaffEntity,
        award: AwardEntity,
        date_str: str,
    ) -> StaffEntity | None:
        """
        Append award association to staff entity.

        Uses StaffRepository's append_award_association method to maintain
        proper entity relationship management patterns.

        :param staff: Staff entity receiving the award
        :param award: Award entity being given
        :param date_str: Date string in format "YYYY-M" or "YYYY-M-D"
        :returns: Updated staff entity with award appended, or None if date parsing fails
        """
        # Parse date using utility function
        award_date = self.__parse_award_date(date_str)
        if award_date is None:
            return None

        # Append association using repository method
        return await self.__staff_repository.append_award_association(
            staff=staff, award=award, date=award_date
        )
