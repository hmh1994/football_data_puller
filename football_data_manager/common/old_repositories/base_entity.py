from uuid import uuid4

from sqlalchemy import Column, String

from football_data_manager.common.enums.source_enum import SourceEnum
from football_data_manager.common.old_repositories import Base


class BaseEntity(Base):
    """
    Base entity model.
    :ivar id: Unique identifier for the entity.
    :param source: Source of the entity data.
    :param source_id: Unique identifier from the source.
    """

    __abstract__ = True

    id = Column(String, nullable=False, primary_key=True)
    source = Column(String, nullable=False)
    source_id = Column(String, nullable=False)

    def __init__(
        self,
        source: SourceEnum,
        source_id: str,
        **kwargs,
    ):
        """
        Initialize the base entity.
        :param source: Source of the entity data.
        :param source_id: Unique identifier from the source.
        :param kwargs: Additional keyword arguments for the entity.
        :return: Instance of the BaseEntity.
        """
        super().__init__(**kwargs)
        self.id = str(uuid4())
        self.source = source.value.upper()
        self.source_id = source_id
