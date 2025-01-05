from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton, Configuration

from football_data_puller.services.config.config_service import ConfigService
from football_data_puller.services.db.db_service import DbService


class ServiceContainer(DeclarativeContainer):
    """
    Service container for the application.
    :ivar container_config: Container's configuration.
    :ivar config_service: Configuration service.
    """

    container_config = Configuration()

    config_service = Singleton(ConfigService, config_path=container_config.config_path)
    db_service = Singleton(DbService, config_service=config_service)
