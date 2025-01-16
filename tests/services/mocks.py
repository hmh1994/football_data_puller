from pathlib import Path
from tempfile import NamedTemporaryFile

from pydantic import HttpUrl

from football_data_puller.services.config.config_service import ConfigService
from tests.utils.random import random_string, random_url


def gen_config_service_mock(
        db_database_name: str | None = None,
        db_database_host: str | None = None,
        db_database_port: int | None = None,
        db_driver_name: str = random_string(10),
        db_user_name: str | None = None,
        db_user_password: str | None = None,
        api_pulselive_key: str | None = None,
        api_pulselive_url: HttpUrl = random_url(20),
        api_pulselive_agent: str | None = None,
) -> ConfigService:
    """
    Generate a fake ConfigService object.
    :param db_database_name: Database name (default: random string.)
    :param db_database_host: Database host (default: random string.)
    :param db_database_port: Database port (default: random number.)
    :param db_driver_name: Database driver name (default: random string.)
    :param db_user_name: Database username (default: random string.)
    :param db_user_password: Database password (default: random string.)
    :param api_pulselive_key: PulseLive API key (default: None.)
    :param api_pulselive_url: PulseLive API URL (default: URL with random host.)
    :param api_pulselive_agent: PulseLive API agent (default: None.)
    :return: A fake configService object.
    """
    config_values = {
        "DB_DATABASE_NAME": db_database_name,
        "DB_DATABASE_HOST": db_database_host,
        "DB_DATABASE_PORT": db_database_port,
        "DB_DRIVER_NAME": db_driver_name,
        "DB_USER_NAME": db_user_name,
        "DB_USER_PASSWORD": db_user_password,
        "API_PULSELIVE_KEY": api_pulselive_key,
        "API_PULSELIVE_URL": api_pulselive_url,
        "API_PULSELIVE_AGENT": api_pulselive_agent,
    }
    with NamedTemporaryFile(mode="w", delete_on_close=True) as fp:
        fp.write("\n".join(f"{k}={str(v)}" for k, v in config_values.items() if v))
        fp.flush()
        config_service = ConfigService(Path(fp.name))
    return config_service
