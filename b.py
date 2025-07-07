from asyncio import run

from football_data_manager.common.services.common_service_container import (
    CommonServiceContainer,
)
from football_data_manager.puller.services.the_athletic.the_athletic_puller_service import (
    TheAthleticPullerService,
)


async def runrun():
    common_service_container = CommonServiceContainer()
    common_service_container.container_config.from_dict(
        {"config_path": "./configs/.env"}
    )
    config_service = common_service_container.config_service()
    db_service = common_service_container.db_service()
    puller_service = TheAthleticPullerService(
        anthropic_config=config_service.api_list.anthropic,
        the_athletic_graphql_config=config_service.api_list.the_athletic_graphql,
        db_service=db_service,
    )
    await puller_service.pull_news()


run(runrun())
