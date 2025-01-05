from sqlalchemy import URL

from football_data_puller.utils.pydantic_helper.config_model import ConfigModel


class DbConfig(ConfigModel):
    """
    Model to store database configuration settings.
    :ivar database_name: Name of the database.
    :ivar database_host: Host URL.
    :ivar database_port: Port number.
    :ivar driver_name: Driver name.
    :ivar user_name: Username.
    :ivar user_password: Password.
    """

    database_name: str
    database_host: str
    database_port: int
    driver_name: str
    user_name: str
    user_password: str

    @property
    def sqlalchemy_url(self) -> URL:
        return URL.create(
            drivername=self.driver_name,
            username=self.user_name,
            password=self.user_password,
            host=self.database_host,
            port=self.database_port,
            database=self.database_name,
        )
