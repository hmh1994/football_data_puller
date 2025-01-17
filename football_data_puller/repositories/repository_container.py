from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration


class RepositoryContainer(DeclarativeContainer):
    container_config = Configuration()
