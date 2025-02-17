from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton, Configuration, Factory

from football_data_manager.common.services.config.config_service import ConfigService
from football_data_manager.common.services.db.db_service import DbService
from football_data_manager.common.services.web_client.web_client_service import (
    WebClientService,
)


class CommonServiceContainer(DeclarativeContainer):
    """
    Common service container for the application.
    :ivar container_config: Container's configuration.
    :ivar config_service: Configuration service.
    :ivar db_service: Database service.
    :ivar web_caller_service: Web client service factory.
    """

    container_config = Configuration()

    config_service = Singleton(ConfigService, config_path=container_config.config_path)
    db_service = Singleton(DbService, config_service=config_service)

    web_caller_service = Factory(WebClientService)
