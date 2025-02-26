from football_data_manager.common.services.config.models.api_config import ApiConfig
from football_data_manager.common.services.db.db_service import DbService
from football_data_manager.puller.services.pulselive.services.pulselive_competitions_service import (
    PulseliveCompetitionsService,
)
from football_data_manager.puller.services.pulselive.services.pulselive_fixture_service import (
    PulseliveFixturesService,
)
from football_data_manager.puller.services.pulselive.services.pulselive_teams_per_compseason_service import (
    PulseliveTeamsPerCompSeasonService,
)
from football_data_manager.puller.services.pulselive.services.pulselive_web_client_service import (
    PulseliveWebClientService,
)


class PulselivePullerService:
    __competition_service: PulseliveCompetitionsService
    __fixture_service: PulseliveFixturesService
    __teams_per_comp_season_service: PulseliveTeamsPerCompSeasonService
    __web_client: PulseliveWebClientService

    def __init__(self, config: ApiConfig, db_service: DbService):
        db_service = db_service
        self.__web_client = PulseliveWebClientService(config)
        self.__competition_service = PulseliveCompetitionsService(
            db_service, self.__web_client
        )
        self.__fixture_service = PulseliveFixturesService(db_service, self.__web_client)
        self.__teams_per_comp_season_service = PulseliveTeamsPerCompSeasonService(
            db_service, self.__web_client
        )

    async def close(self):
        """
        Closes the service.
        """
        await self.__web_client.close()

    async def pull_data(self):
        """
        Pulls data from the Pulselive API.
        """
        # 1st job
        await self.__competition_service.pull_competitions()
        # 2nd job
        await self.__teams_per_comp_season_service.pull_players()
        await self.__fixture_service.pull_fixtures()
