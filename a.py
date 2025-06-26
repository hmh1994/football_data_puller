from asyncio import run
from pathlib import Path

from football_data_manager.common.services.config.config_service import ConfigService
from football_data_manager.common.services.db.db_service import DbService


async def runrun():

    config_service = ConfigService(Path("./configs/.env"))
    db_service = DbService(config_service)


run(runrun())
