from sqlalchemy import Column, String

from football_data_manager.common.new_repositories.constants import OFFICIALS_TABLE_NAME
from football_data_manager.common.old_repositories.pulselive_entity import (
    PulseliveEntity,
)


class OfficialEntity(PulseliveEntity):
    __tablename__ = OFFICIALS_TABLE_NAME

    name_en = Column(String, nullable=False)
    name_kr = Column(String, nullable=False)
