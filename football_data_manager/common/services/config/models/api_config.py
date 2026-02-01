from pydantic import HttpUrl

from football_data_manager.common.utils.pydantic_helper.config_model import ConfigModel


class ApiConfig(ConfigModel):
    """
    Model to store API configuration settings.
    :ivar agent: User agent.
    :ivar key: API key.
    :ivar url: URL of the API.
    """

    agent: str | None = None
    key: str | None = None
    url: HttpUrl | None = None
