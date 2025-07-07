from pydantic import BaseModel

from football_data_manager.common.services.config.models.api_config import ApiConfig
from football_data_manager.common.utils.type_helper.dict_helper import (
    extract_without_key,
)


class ApiListConfig(BaseModel):
    """
    Model to store List of API configuration settings.
    :ivar pulselive: Pulselive API configuration.
    """

    anthropic: ApiConfig
    open_ai: ApiConfig
    pulselive: ApiConfig
    the_athletic_graphql: ApiConfig

    def __init__(self, **data):
        super().__init__(
            anthropic=ApiConfig(**extract_without_key("ANTHROPIC", data)),
            open_ai=ApiConfig(**extract_without_key("OPEN_AI", data)),
            pulselive=ApiConfig(**extract_without_key("PULSELIVE", data)),
            the_athletic_graphql=ApiConfig(
                **extract_without_key("THE_ATHLETIC_GRAPHQL", data)
            ),
        )
