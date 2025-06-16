from typing import Self
from uuid import uuid4
from xmlrpc.client import DateTime

from sqlalchemy import Column, String

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
    source = Column(String, nullable=False)
    source_id = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    def __init__(
        self,
        source: SourceEnum,
        source_id: str,
        **kwargs,
    ) -> Self:
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
        self.source = source.value.upper()
        self.source_id = source_id
        self.updated_at = now

    def get_id(self) -> str:
        """
        Get the unique identifier of the entity.
        :return: Unique identifier as a string.
        """
        return self.id
