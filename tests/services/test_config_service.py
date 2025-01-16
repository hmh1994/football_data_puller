from football_data_puller.services.config.config_service import ConfigService
from football_data_puller.utils.constants import CONFIG_PATH
from tests.services.mocks import gen_config_service_mock
from tests.utils.random import random_string, random_number, random_url


class TestConfigService:
    """
    Tests for the ConfigService.
    """

    def test_sample_config(self):
        """
        Tests the sample config.
        """
        assert isinstance(
            ConfigService(CONFIG_PATH.with_suffix(".sample")), ConfigService
        ), "Sample config not loaded."

    def test_config_values(self):
        """
        Tests the config values are loaded correctly.
        """
        expect_values = {
            "db_database_name": random_string(20),
            "db_database_host": random_string(10),
            "db_database_port": random_number(4),
            "db_driver_name": random_string(10),
            "db_user_name": random_string(10),
            "db_user_password": random_string(15),
            "api_pulselive_key": None,
            "api_pulselive_url": random_url(20),
            "api_pulselive_agent": None,
        }
        config_service_mock = gen_config_service_mock(**expect_values)
        actual_values = {
            "db_database_name": config_service_mock.db.database_name,
            "db_database_host": config_service_mock.db.database_host,
            "db_database_port": config_service_mock.db.database_port,
            "db_driver_name": config_service_mock.db.driver_name,
            "db_user_name": config_service_mock.db.user_name,
            "db_user_password": config_service_mock.db.user_password,
            "api_pulselive_key": config_service_mock.api_list.pulselive.key,
            "api_pulselive_url": config_service_mock.api_list.pulselive.url,
            "api_pulselive_agent": config_service_mock.api_list.pulselive.agent,
        }
        assert len(expect_values) == len(actual_values), "Config keys mismatched."
        for key, value in expect_values.items():
            assert value == actual_values[key], (
                    f"Config value mismatched for {key}" +
                    f" (expect: {value}, actual: {actual_values[key]}).")
