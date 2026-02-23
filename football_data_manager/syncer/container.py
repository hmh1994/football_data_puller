from pathlib import Path

from dependency_injector import containers, providers

from football_data_manager.common.services.config.config_service import ConfigService
from football_data_manager.common.utils.constants import CONFIG_PATH
from football_data_manager.merger.container import MergerContainer
from football_data_manager.puller.container import PullerContainer
from football_data_manager.repository.container import RepositoryContainer


class SyncContainer(containers.DeclarativeContainer):
    """DI container for sync orchestration layer."""

    config_service = providers.Dependency(instance_of=ConfigService)

    repository_container = providers.Container(
        RepositoryContainer,
        config_service=config_service,
    )
    puller_container = providers.Container(PullerContainer)
    merger_container = providers.Container(
        MergerContainer,
        config_service=config_service,
        repository_container=repository_container,
        puller_container=puller_container,
    )


async def create_sync_container(
    config_path: Path = CONFIG_PATH,
    validate_connection: bool = False,
) -> SyncContainer:
    """Build sync container and configure nested puller container."""
    config_service = ConfigService(config_path)
    container = SyncContainer(config_service=config_service)
    container.puller_container().config.from_dict(config_service.api_list.model_dump())

    if validate_connection:
        session_factory = container.repository_container().session_factory()
        if not await session_factory.check_connection():
            raise ConnectionError("Failed to connect to database")

    return container
