from pathlib import Path

from dotenv import dotenv_values

from football_data_puller.services.config.models.api_list_config import (
    ApiListConfig,
)
from football_data_puller.services.config.models.db_config import DbConfig
from football_data_puller.utils.type_helper.dict_helper import extract_without_key


class ConfigService:
    """
    Service class to handle configuration settings.
    :param config_path: Path to the configuration.
    :ivar db: Database config.
    :ivar api_list: List of API config.
    """

    db: DbConfig
    api_list: ApiListConfig

    def __init__(self, config_path: Path):
        data = dotenv_values(config_path)
        self.db = DbConfig(**extract_without_key("DB", data))
        self.api_list = ApiListConfig(**extract_without_key("API", data))
