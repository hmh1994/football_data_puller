from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.repositories import Base
from football_data_manager.common.repositories.awards.award_entity import AwardEntity
from football_data_manager.common.repositories.constants import (
    STAFF_AWARD_ASSOCIATION_TABLE_NAME,
)
from football_data_manager.common.repositories.staffs.staff_entity import StaffEntity


class StaffAwardAssociation(Base):
    """
    Association class for staff awards.

    Associates awards with staff members (coaches, managers) for specific dates.
    Used to track Manager of the Month, Manager of the Season, and other
    staff-related awards.

    :ivar award_id: Foreign key to the award entity
    :ivar staff_id: Foreign key to the staff entity
    :ivar date: Date when the award was given
    :ivar staff: Relationship to staff entity
    """

    __tablename__ = STAFF_AWARD_ASSOCIATION_TABLE_NAME

    AWARD_COLLECTION_NAME = "award_associations"

    award_id = Column(
        String,
        ForeignKey(AwardEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    staff_id = Column(
        String,
        ForeignKey(StaffEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    date = Column(DateTime, nullable=False, primary_key=True)
    staff = relationship(
        "StaffEntity",
        backref=backref(
            name=AWARD_COLLECTION_NAME,
            lazy="noload",
            cascade="all, delete-orphan",
            order_by="StaffAwardAssociation.date",
        ),
    )

    def __init__(self, staff: StaffEntity, award: AwardEntity, date: datetime):
        """
        Initialize a new staff award association.

        :param staff: Staff entity receiving the award
        :param award: Award entity being given
        :param date: Date when the award was given
        """
        super().__init__()
        self.award_id = award.id
        self.date = date
        self.staff_id = staff.id
