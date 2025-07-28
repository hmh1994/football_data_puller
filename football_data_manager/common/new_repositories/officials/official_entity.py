from hashlib import md5

from sqlalchemy import Column, String

from football_data_manager.common.new_repositories.constants import OFFICIALS_TABLE_NAME
from football_data_manager.common.new_repositories.pulselive_entity import (
    PulseliveEntity,
)


class OfficialEntity(PulseliveEntity):
    __tablename__ = OFFICIALS_TABLE_NAME

    display_name_en = Column(String, nullable=False)
    display_name_kr = Column(String, nullable=False)
    full_name = Column(String, nullable=False)

    def __init__(self, display_name_en: str, display_name_kr: str, full_name: str):
        temporary_source_id = md5(display_name_en.encode("utf-8")).hexdigest()
        super().__init__(source_id=str(int(temporary_source_id, 16) % 2**16))
        self.display_name_en = display_name_en
        self.display_name_kr = display_name_kr
        self.full_name = full_name
