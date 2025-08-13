from datetime import datetime

from football_data_manager.common.repositories.competitions.competition_entity import (
    CompetitionEntity,
)
from football_data_manager.common.repositories.competitions.competition_repository import (
    CompetitionRepository,
)
from football_data_manager.common.repositories.repository_container import (
    CommonRepositoryContainer,
)
from football_data_manager.common.repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.repositories.seasons.season_repository import (
    SeasonRepository,
)
from football_data_manager.common.utils.type_helper.datetime_helper import (
    create_utc_from_string,
)
from football_data_manager.puller.services.pulselive_new.components.pulselive_new_webclient import (
    PulseliveNewWebclient,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_match_response import (
    PulseliveNewMatchResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_competition_detail_season_response import (
    PulseliveNewCompetitionDetailSeasonResponse,
)


class PulseliveNewSeasonPuller:
    """
    Service for pulling season data from PulseLive v1 competition details API.

    Handles fetching season information for a specific competition and persisting
    to the database. Processes season names to extract year boundaries and creates
    temporal data for season entities.

    :ivar __season_repository: Repository for season database operations
    :ivar __competition_repository: Repository for competition database operations
    :ivar __webclient: HTTP client for PulseLive API requests
    """

    __season_repository: SeasonRepository
    __competition_repository: CompetitionRepository
    __webclient: PulseliveNewWebclient

    def __init__(
        self,
        repository_container: CommonRepositoryContainer,
        pulselive_service: PulseliveNewWebclient,
    ):
        """
        Initialize the season puller.

        :param service_container: Container with common services
        :param repository_container: Container with repository instances
        :param pulselive_service: HTTP client for PulseLive API
        """
        self.__season_repository = repository_container.season_repository()
        self.__competition_repository = repository_container.competition_repository()
        self.__webclient = pulselive_service

    async def pull_seasons_for_competition(
        self, competition: CompetitionEntity
    ) -> list[SeasonEntity]:
        """
        Pull all seasons for a specific competition from the PulseLive API.

        Retrieves competition details including all available seasons,
        processes them, and stores them in the database.

        :param competition: Competition entity to pull seasons for
        :returns: List of season entities created or updated
        """
        # Get competition details including seasons
        response = await self.__webclient.get_v1_competition_details(
            competition.source_id
        )

        # Process seasons
        seasons = await self.__process_seasons(response.seasons, competition)
        return seasons

    async def __process_seasons(
        self,
        season_items: list[PulseliveNewCompetitionDetailSeasonResponse],
        competition: CompetitionEntity,
    ) -> list[SeasonEntity]:
        """
        Process season items from API response into database entities.

        Converts API response objects to season entities with extracted year boundaries
        and temporal data, then persists them to the database.

        :param season_items: List of season items from API response
        :param competition: Competition entity these seasons belong to
        :returns: List of processed season entities
        """
        seasons = []

        for item in season_items:
            try:
                # Check if season already exists
                existing_season = await self.__season_repository.read_by_pulselive_id(
                    source_id=SeasonEntity.get_source_id(competition, item.id)
                )

                if existing_season is not None:
                    seasons.append(existing_season)
                    continue

                # Extract year boundaries from season name (e.g., "Season 2024/2025")
                year_start, year_end = self.__extract_years_from_season_name(
                    item.season
                )

                # Generate season abbreviation (e.g., "24/25")
                abbreviation = f"{str(year_start)[-2:]}/{str(year_end)[-2:]}"

                # Get actual season dates from match data
                date_start, date_end = await self.__get_season_dates(
                    competition.source_id, item.id
                )

                # Create new season entity
                season = SeasonEntity(
                    abbreviation=abbreviation,
                    competition=competition,
                    date_end=date_end,
                    date_start=date_start,
                    season_source_id=item.id,
                    year_end=year_end,
                    year_start=year_start,
                )

                # Save to database
                created_season = await self.__season_repository.create(season)
                if created_season is not None:
                    seasons.append(created_season)
            except ValueError as error:
                print(
                    f"Error processing season '{item.season}' of {competition.abbreviation}: {error}"
                )

        return seasons

    @staticmethod
    def __extract_years_from_season_name(season_name: str) -> tuple[int, int]:
        """
        Extract start and end years from season name.

        Parses season names like "Season 2024/2025" to extract the year boundaries.
        Handles both full year format (2024/2025) and abbreviated format (24/25).

        :param season_name: Season name string (e.g., "Season 2024/2025")
        :returns: Tuple of (start_year, end_year)
        :raises ValueError: If season name format is not recognized
        """
        # Remove "Season " prefix and extract year part
        year_part = season_name.replace("Season ", "").strip()

        if "/" in year_part:
            parts = year_part.split("/")
            if len(parts) == 2:
                year_start = int(parts[0])
                year_end_str = parts[1]

                # Handle abbreviated year format (e.g., "24" in "2024/25")
                if len(year_end_str) == 2:
                    year_end = int(f"{str(year_start)[:2]}{year_end_str}")
                else:
                    year_end = int(year_end_str)

                return year_start, year_end

        raise ValueError(f"Cannot parse season name: {season_name}")

    async def __get_season_dates(
        self, competition_id: str, season_id: str
    ) -> tuple[datetime, datetime]:
        """
        Get actual season start and end dates from match data.

        Fetches the earliest match from matchweek 1 for season start date,
        and uses binary search to find the latest match from the last
        available matchweek for season end date.

        :param competition_id: Competition identifier
        :param season_id: Season identifier
        :returns: Tuple of (season_start_date, season_end_date)
        :raises ValueError: If no match data is found for the season
        """
        # Get season start date from matchweek 1
        date_start = await self.__get_season_start_date(competition_id, season_id)

        # Get season end date using binary search from matchweek 50
        date_end = await self.__get_season_end_date(competition_id, season_id)

        return date_start, date_end

    async def __get_season_start_date(
        self, competition_id: str, season_id: str
    ) -> datetime:
        """
        Get season start date from the earliest match in matchweek 1.

        :param competition_id: Competition identifier
        :param season_id: Season identifier
        :returns: Season start date
        :raises ValueError: If no matches found in matchweek 1
        """
        try:
            # Get all matches from matchweek 1
            all_matches = await self.__get_all_matches_for_matchweek(
                competition_id, season_id, 1
            )

            if not all_matches:
                raise ValueError(
                    f"No matches found in matchweek 1 for season {season_id}"
                )

            # Find the earliest kickoff time and convert to UTC
            earliest_kickoff = min(
                create_utc_from_string(match.kickoff, match.kickoff_timezone)
                for match in all_matches
            )

            return earliest_kickoff

        except Exception as e:
            raise ValueError(f"Error getting season start date: {str(e)}")

    async def __get_season_end_date(
        self, competition_id: str, season_id: str
    ) -> datetime:
        """
        Get season end date using binary search to find the last matchweek.

        Starts from matchweek 50 and searches backwards to find the highest
        numbered matchweek with available matches, then returns the latest
        kickoff time from that matchweek.

        :param competition_id: Competition identifier
        :param season_id: Season identifier
        :returns: Season end date
        :raises ValueError: If no matches found in any matchweek
        """
        try:
            # Binary search to find the last matchweek with matches (returns matches)
            last_matchweek, all_matches = await self.__find_last_matchweek_with_matches(
                competition_id, season_id, start_week=50
            )

            if last_matchweek is None or not all_matches:
                raise ValueError(f"No matchweeks found for season {season_id}")

            # Find the latest kickoff time and convert to UTC
            latest_kickoff = max(
                create_utc_from_string(match.kickoff, match.kickoff_timezone)
                for match in all_matches
            )

            return latest_kickoff

        except Exception as e:
            raise ValueError(f"Error getting season end date: {str(e)}")

    async def __find_last_matchweek_with_matches(
        self, competition_id: str, season_id: str, start_week: int = 50
    ) -> tuple[int | None, list[PulseliveNewMatchResponse]]:
        """
        Use binary search to find the highest matchweek number with matches and return the matches.

        Optimized version that returns both the matchweek number and all matches from that matchweek,
        avoiding the need for an additional API call to fetch matches.

        :param competition_id: Competition identifier
        :param season_id: Season identifier
        :param start_week: Starting week for binary search
        :returns: Tuple of (last_matchweek_number, all_matches) or None if none found
        """
        # First, check if the start_week has matches
        start_week_matches = await self.__get_all_matches_for_matchweek(
            competition_id, season_id, start_week
        )

        if start_week_matches:
            # Search upwards from start_week to find the actual maximum
            current_week = start_week
            current_matches = start_week_matches

            while True:
                next_week_matches = await self.__get_all_matches_for_matchweek(
                    competition_id, season_id, current_week + 1
                )
                if not next_week_matches:
                    break
                current_week += 1
                current_matches = next_week_matches

            return current_week, current_matches

        # Binary search downwards from start_week
        left, right = 1, start_week
        last_valid_week = None
        last_valid_matches = None

        while left <= right:
            mid = (left + right) // 2
            mid_matches = await self.__get_all_matches_for_matchweek(
                competition_id, season_id, mid
            )

            if mid_matches:
                last_valid_week = mid
                last_valid_matches = mid_matches
                left = mid + 1  # Search for higher week numbers
            else:
                right = mid - 1  # Search for lower week numbers

        if last_valid_week is not None and last_valid_matches is not None:
            return last_valid_week, last_valid_matches

        return None, []

    async def __get_all_matches_for_matchweek(
        self, competition_id: str, season_id: str, matchweek_number: int
    ) -> list[PulseliveNewMatchResponse]:
        """
        Get all matches for a specific matchweek using pagination.

        :param competition_id: Competition identifier
        :param season_id: Season identifier
        :param matchweek_number: Matchweek number to fetch
        :returns: List of all matches in the matchweek
        """
        all_matches = []
        _next = None

        while True:
            response = await self.__webclient.get_v1_matchweek_matches(
                competition_id, season_id, matchweek_number, limit=50, _next=_next
            )

            all_matches.extend(response.data)

            if response.pagination.next is None:
                break

            _next = response.pagination.next

        return all_matches
