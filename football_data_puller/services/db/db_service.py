from typing import Generator

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

from football_data_puller.services.config.config_service import ConfigService


class DbService:
    """
    Database service class to handle database operations.
    :param config_service: Configuration service.
    """

    __engine: Engine
    __session_maker: sessionmaker

    def __init__(self, config_service: ConfigService):
        self.__engine = create_engine(
            config_service.db.sqlalchemy_url, pool_pre_ping=True
        )
        self.__session = sessionmaker(bind=self.__engine)

    def check_connection(self) -> bool:
        try:
            self.__engine.connect()
            return True
        except Exception:
            return False

    def create_db_session(self) -> Generator[Session, None, None]:
        db = self.__session()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
