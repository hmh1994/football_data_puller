from argparse import ArgumentParser
from asyncio import run

from football_data_puller.repositories import Base
from football_data_puller.services.service_container import ServiceContainer
from tests.repositories.sample_data.competition_sample_data import CompetitionSampleData
from tests.repositories.sample_data.fixture_sample_data import FixtureSampleData
from tests.repositories.sample_data.ground_sample_data import GroundSampleData
from tests.repositories.sample_data.player_sample_data import PlayerSampleData
from tests.repositories.sample_data.season_sample_data import SeasonSampleData
from tests.repositories.sample_data.standing_sample_data import StandingSampleData
from tests.repositories.sample_data.team_sample_data import TeamSampleData

OPERATION_DICT = {"health": lambda: print("I'm healthy!"), "test": lambda: run(test())}
"""The dictionary of operations application supports."""


async def test():
    service_container = ServiceContainer()
    service_container.container_config.from_dict({"config_path": "./configs/.env"})
    db_service = service_container.db_service()
    async with db_service.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await CompetitionSampleData().initialize(db_service, True)
    await FixtureSampleData().initialize(db_service, True)
    await GroundSampleData().initialize(db_service, True)
    await PlayerSampleData().initialize(db_service, True)
    await SeasonSampleData().initialize(db_service, True)
    await StandingSampleData().initialize(db_service, True)
    await TeamSampleData().initialize(db_service, True)


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
