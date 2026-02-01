from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton, Configuration

from football_data_manager.common.services.config.config_service import ConfigService
from football_data_manager.common.services.db.db_service import DbService
from football_data_manager.common.services.translator.translatorService import (
    TranslatorService,
)


class CommonServiceContainer(DeclarativeContainer):
    """
    Common service container for the application.
    :ivar container_config: Container's configuration.
    :ivar config_service: Configuration service.
    :ivar db_service: Database service.
    """

    container_config = Configuration()

    config_service = Singleton(ConfigService, config_path=container_config.config_path)
    db_service = Singleton(DbService, config_service=config_service)
    translator_service = Singleton(TranslatorService, config_service=config_service)
