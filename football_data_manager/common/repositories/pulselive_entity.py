from football_data_manager.common.enums.source_enum import SourceEnum
from football_data_manager.common.repositories.base_entity import BaseEntity


class PulseliveEntity(BaseEntity):
    """
    Pulselive entity model.
    :ivar id: Unique identifier for the entity.
    :ivar source: Source of the entity data, set to PULSELIVE.
    :param source_id: Unique identifier from the source.
    """

    __abstract__ = True

    def __init__(self, source_id: str):
        """
        Initialize the Pulselive entity.
        :param source_id: Unique identifier from the source.
        :return: Instance of the PulseliveEntity.
        """
        super().__init__(
            source=SourceEnum.PULSELIVE,
            source_id=source_id,
        )
