from asyncio import run

from football_data_manager.common.services.common_service_container import (
    CommonServiceContainer,
)
from football_data_manager.common.services.config.config_service import ConfigService
from football_data_manager.common.services.db.db_service import DbService
from football_data_manager.puller.services.pulselive.services.pulselive_fixture_service import (
    PulseliveFixturesService,
)
from football_data_manager.puller.services.pulselive.services.pulselive_web_client_service import (
    PulseliveWebClientService,
)
from football_data_manager.puller.services.the_athletic.the_athletic_puller_service import (
    TheAthleticPullerService,
)


async def update_news(config_service: ConfigService, db_service: DbService):
    puller_service = TheAthleticPullerService(
        anthropic_config=config_service.api_list.anthropic,
        the_athletic_graphql_config=config_service.api_list.the_athletic_graphql,
        db_service=db_service,
    )
    await puller_service.pull_news()


async def update_fixtures(
    db_service: DbService, pulselive_service: PulseliveWebClientService
):
    puller_service = PulseliveFixturesService(db_service, pulselive_service)
    await puller_service.pull_fixtures()


async def runrun():
    common_service_container = CommonServiceContainer()
    common_service_container.container_config.from_dict(
        {"config_path": "./configs/.env"}
    )
    config_service = common_service_container.config_service()
    db_service = common_service_container.db_service()
    web_client_service = PulseliveWebClientService(config_service.api_list.pulselive)
    await update_news(config_service, db_service)
    # await update_fixtures(db_service, web_client_service)


run(runrun())
