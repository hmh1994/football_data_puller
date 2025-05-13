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

    open_ai: ApiConfig
    pulselive: ApiConfig
    the_athletic: ApiConfig

    def __init__(self, **data):
        super().__init__(
            open_ai=ApiConfig(**extract_without_key("OPEN_AI", data)),
            pulselive=ApiConfig(**extract_without_key("PULSELIVE", data)),
            the_athletic=ApiConfig(**extract_without_key("THE_ATHLETIC", data))
        )
