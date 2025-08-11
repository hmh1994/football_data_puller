from football_data_manager.common.repositories.competitions.competition_entity import (
    CompetitionEntity,
)
from football_data_manager.common.repositories.competitions.competition_repository import (
    CompetitionRepository,
)
from football_data_manager.common.repositories.repository_container import (
    CommonRepositoryContainer,
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
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_competition_item_response import (
    PulseliveNewCompetitionItemResponse,
)


class PulseliveNewCompetitionPuller:
    """
    Service for pulling competition data from PulseLive v1 API.

    Handles fetching competition information, translating content, and persisting
    to the database. Supports paginated data retrieval and batch processing.

    :ivar __competition_repository: Repository for competition database operations
    :ivar __translator: Service for translating competition names
    :ivar __webclient: HTTP client for PulseLive API requests
    """

    __competition_repository: CompetitionRepository
    __translator: TranslatorService
    __webclient: PulseliveNewWebclient

    id_filter: list[str] = [
        "1",  # EN_FA: English FA Cup
        "2",  # EN_LC: English League Cup
        "5",  # EU_CL: UEFA Champions League
        "6",  # EU_EL: UEFA Europa League
        "8",  # EN_PR: Premier League
        "1007",  # IG_OF: Other Club Friendlies
        "1125",  # EU_CF: UEFA Conference League
    ]

    def __init__(
        self,
        service_container: CommonServiceContainer,
        repository_container: CommonRepositoryContainer,
        pulselive_service: PulseliveNewWebclient,
    ):
        """
        Initialize the competition puller.

        :param service_container: Container with common services like translator
        :param repository_container: Container with repository instances
        :param pulselive_service: HTTP client for PulseLive API
        """
        self.__competition_repository = repository_container.competition_repository()
        self.__translator = service_container.translator_service()
        self.__webclient = pulselive_service

    async def pull_all_competitions(self) -> list[CompetitionEntity]:
        """
        Pull all competitions from the PulseLive API.

        Retrieves all competitions using pagination, processes them,
        and stores them in the database.

        :returns: List of all competition entities created or updated
        """
        all_competitions = []
        cursor = None

        while True:
            competitions, cursor = await self.pull_competitions(limit=50, cursor=cursor)
            all_competitions.extend(competitions)
            if cursor is None:
                break

        return all_competitions

    async def pull_competitions(
        self, limit: int = 10, cursor: str | None = None
    ) -> tuple[list[CompetitionEntity], str | None]:
        """
        Pull a single page of competitions from the PulseLive API.

        :param limit: Maximum number of competitions to retrieve
        :param cursor: Pagination cursor for the next page
        :returns: Tuple of (competitions list, next page cursor)
        """
        response = await self.__webclient.get_v1_competitions(
            limit=limit, cursor=cursor
        )
        competitions = await self.__process_competitions(response.data)
        return competitions, response.pagination.next

    async def __process_competitions(
        self, competition_items: list[PulseliveNewCompetitionItemResponse]
    ) -> list[CompetitionEntity]:
        """
        Process competition items from API response into database entities.

        Converts API response objects to competition entities with translated names
        and persists them to the database.

        :param competition_items: List of competition items from API response
        :returns: List of processed competition entities
        """
        competitions = []

        for item in competition_items:
            if item.id not in self.id_filter:
                continue

            # Check if competition already exists
            existing_competition = (
                await self.__competition_repository.read_by_pulselive_id(
                    source_id=item.id
                )
            )

            if existing_competition is not None:
                competitions.append(existing_competition)
                continue

            # Translate competition name to Korean
            name_kr = await self.__translator.translate_word(item.name)

            # Create new competition entity
            competition = CompetitionEntity(
                abbreviation=item.code,
                name_en=item.name,
                name_kr=name_kr,
                source_id=item.id,
            )

            # Save to database
            created_competition = await self.__competition_repository.create(
                competition
            )
            if created_competition is not None:
                competitions.append(created_competition)

        return competitions
