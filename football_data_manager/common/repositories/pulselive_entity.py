from football_data_manager.common.enums.source_enum import SourceEnum
from football_data_manager.common.repositories.base_entity import BaseEntity


class PulseliveEntity(BaseEntity):
    """
    Pulselive entity model.

    Abstract base for entities sourced from the Pulselive API.
    Automatically sets source to PULSELIVE.
    """

    __abstract__ = True

    def __init__(self, source_id: str):
        """
        Initialize the Pulselive entity.

        :param source_id: Unique identifier from the source
        """
        super().__init__(
            source=SourceEnum.PULSELIVE,
            source_id=source_id,
        )
