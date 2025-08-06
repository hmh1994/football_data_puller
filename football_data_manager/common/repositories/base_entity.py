from uuid import uuid4

from sqlalchemy import Column, String, DateTime, Enum

from football_data_manager.common.enums.source_enum import SourceEnum
from football_data_manager.common.repositories import Base
from football_data_manager.common.utils.type_helper.datetime_helper import (
    create_utc_now,
)


class BaseEntity(Base):
    """
    Base entity model.
    :ivar id: Unique identifier for the entity.
    :param source: Source of the entity data.
    :param source_id: Unique identifier from the source.
    """

    __abstract__ = True

    id = Column(String, nullable=False, primary_key=True)
    source = Column(Enum(SourceEnum), nullable=False)
    source_id = Column(String, nullable=False, unique=True, index=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

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
        now = create_utc_now()
        super().__init__(**kwargs)
        self.id = str(uuid4())
        self.created_at = now
        self.source = source
        self.source_id = source_id
        self.updated_at = now
