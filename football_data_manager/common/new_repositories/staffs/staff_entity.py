from sqlalchemy import Column, String

from football_data_manager.common.new_repositories.constants import STAFFS_TABLE_NAME
from football_data_manager.common.new_repositories.pulselive_entity import PulseliveEntity


class StaffEntity(PulseliveEntity):
    __tablename__ = STAFFS_TABLE_NAME

    name_en = Column(String, nullable=False)
    name_kr = Column(String, nullable=False)
