from argparse import ArgumentParser
from asyncio import run

from football_data_manager.common.old_repositories import Base
from football_data_manager.common.services.common_service_container import (
    CommonServiceContainer,
)
from football_data_manager.puller.services.puller_service_container import (
    PullerServiceContainer,
)

OPERATION_DICT = {"health": lambda: print("I'm healthy!"), "test": lambda: run(test())}
"""The dictionary of operations application supports."""


async def test():
    common_service_container = CommonServiceContainer()
    common_service_container.container_config.from_dict(
        {"config_path": "./configs/.env"}
    )
    config_service = common_service_container.config_service()
    db_service = common_service_container.db_service()
    async with db_service.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    puller_service_container = PullerServiceContainer()
    puller_service_container.container_config.from_dict(
        {
            "openai_config": config_service.api_list.open_ai,
            "the_athletic_config": config_service.api_list.the_athletic,
            "pulselive_config": config_service.api_list.pulselive,
            "db_service": db_service,
        }
    )
    # pulselive_service = puller_service_container.pulselive_service()
    # await pulselive_service.pull_data()
    # await pulselive_service.close()
    the_athletic_service = puller_service_container.the_athletic_service()
    await the_athletic_service.pull_news()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "operation",
        type=str,
        choices=OPERATION_DICT.keys(),
        help="The operation to run.",
    )
    args = parser.parse_args()
    OPERATION_DICT[args.operation]()
