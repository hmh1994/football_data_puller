from pydantic import BaseModel

from football_data_puller.services.config.models.api_config import ApiConfig
from football_data_puller.utils.type_helper.dict_helper import extract_without_key


class ApiListConfig(BaseModel):
    """
    Model to store List of API configuration settings.
    :ivar pulselive: Pulselive API configuration.
    """

    pulselive: ApiConfig

    def __init__(self, **data):
        super().__init__(pulselive=ApiConfig(**extract_without_key("PULSELIVE", data)))
