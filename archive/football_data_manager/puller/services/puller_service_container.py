from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Singleton

from football_data_manager.puller.services.pulselive.pulselive_puller_service import (
    PulselivePullerService,
)
from football_data_manager.puller.services.the_athletic.the_athletic_puller_service import (
    TheAthleticPullerService,
)


class PullerServiceContainer(DeclarativeContainer):
    """
    Puller service container for the application.
    :ivar container_config: Container's configuration.
    """

    container_config = Configuration()

    pulselive_service = Singleton(
        PulselivePullerService,
        config=container_config.pulselive_config,
        db_service=container_config.db_service,
    )

    the_athletic_service = Singleton(
        TheAthleticPullerService,
        openai_config=container_config.openai_config,
        the_athletic_config=container_config.the_athletic_config,
        db_service=container_config.db_service,
    )
