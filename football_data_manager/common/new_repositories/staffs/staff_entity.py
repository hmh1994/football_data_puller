from sqlalchemy import Column, String

from football_data_manager.common.new_repositories.constants import STAFFS_TABLE_NAME
from football_data_manager.common.new_repositories.pulselive_entity import (
    PulseliveEntity,
)


class StaffEntity(PulseliveEntity):
    __tablename__ = STAFFS_TABLE_NAME

    display_name_en = Column(String, nullable=False)
    display_name_kr = Column(String, nullable=False)
    full_name = Column(String, nullable=False)

    def __init__(
        self, display_name_en: str, display_name_kr: str, full_name: str, source_id: str
    ):
        super().__init__(source_id=source_id)
        self.display_name_en = display_name_en
        self.display_name_kr = display_name_kr
        self.full_name = full_name
