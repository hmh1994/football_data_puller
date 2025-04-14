from abc import abstractmethod

from sqlalchemy import Column, String

from football_data_manager.common.repositories import Base
from football_data_manager.common.utils.class_helper.class_property import classproperty


class BaseEntity(Base):
    """
    Base entity model.
    """

    __abstract__ = True

    id = Column(String, primary_key=True)

    @classproperty
    @abstractmethod
    def prefix(cls) -> str:
        """
        Get the prefix of the entity.
        :return: Entity prefix.
        """
        pass

    @classmethod
    def get_id(cls, api_id: str) -> str:
        """
        Get the ID of the entity.
        :param api_id: The ID of the entity from the API.
        :return: Entity ID.
        """
        assert cls.prefix is not None, "Entity prefix is not set."
        return f"{cls.prefix}_{api_id}"

    @property
    def api_id(self) -> str:
        """
        Get the API ID of the entity.
        :return: API ID.
        """
        assert self.prefix is not None, "Entity prefix is not set."
        return self.id.removeprefix(f"{self.prefix}_")
