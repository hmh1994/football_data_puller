from uuid import uuid4

from sqlalchemy import String, DateTime, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from football_data_manager.common.enums.source_enum import SourceEnum
from football_data_manager.common.utils.type_helper.datetime_helper import (
    create_utc_now,
)


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 declarative base class."""

    pass


class BaseEntity(Base):
    """
    Base entity model.

    All entities inherit from this class, which provides common fields
    for identification, source tracking, and timestamps.

    :ivar id: Unique identifier (UUID)
    :ivar source: Data source identifier
    :ivar source_id: Unique identifier from the source
    :ivar created_at: Creation timestamp (UTC)
    :ivar updated_at: Last modification timestamp (UTC)
    """

    __abstract__ = True

    id: Mapped[str] = mapped_column(String, primary_key=True)
    source: Mapped[SourceEnum] = mapped_column(Enum(SourceEnum), nullable=False)
    source_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    def __init__(
        self,
        source: SourceEnum,
        source_id: str,
        **kwargs,
    ):
        """
        Initialize the base entity.

        :param source: Source of the entity data
        :param source_id: Unique identifier from the source
        :param kwargs: Additional keyword arguments
        """
        now = create_utc_now()
        super().__init__(**kwargs)
        self.id = str(uuid4())
        self.created_at = now
        self.source = source
        self.source_id = source_id
        self.updated_at = now


class PulseliveEntity(BaseEntity):
    """
    Pulselive entity model.

    Abstract base for entities sourced from the Pulselive API.
    Automatically sets source to PULSELIVE.
    """

    __abstract__ = True

    def __init__(self, source_id: str, **kwargs):
        """
        Initialize the Pulselive entity.

        :param source_id: Unique identifier from the source
        """
        super().__init__(
            source=SourceEnum.PULSELIVE,
            source_id=source_id,
            **kwargs,
        )
