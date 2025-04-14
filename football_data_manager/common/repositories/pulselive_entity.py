from abc import ABCMeta, abstractmethod

from football_data_manager.common.repositories.base_entity import BaseEntity
from football_data_manager.common.utils.class_helper.class_property import classproperty


class PulseliveEntity(BaseEntity, metaclass=ABCMeta):
    """
    Pulselive entity model.
    """

    __abstract__ = True

    @classproperty
    @abstractmethod
    def entity_type(cls) -> str:
        """
        Get the prefix of the entity.
        :return: Entity prefix.
        """
        pass

    @classproperty
    def prefix(cls) -> str:
        """
        Get the prefix of the entity.
        :return: Entity prefix.
        """
        assert cls.entity_type is not None, "Entity type is not set."
        return f"PULSELIVE_{cls.entity_type}"
