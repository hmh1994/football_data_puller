from datetime import datetime

from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from football_data_manager.repository.entities.base import Base
from football_data_manager.repository.entities.staffs import StaffEntity

STAFF_AWARD_ASSOCIATION_TABLE_NAME = "staff_award_association"


class StaffAwardAssociation(Base):
    """
    Association class for staff awards.

    :ivar award_id: Foreign key to the award entity
    :ivar staff_id: Foreign key to the staff entity
    :ivar date: Date when the award was given
    """

    __tablename__ = STAFF_AWARD_ASSOCIATION_TABLE_NAME

    AWARD_COLLECTION_NAME = "award_associations"

    award_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("awards.id", ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    staff_id: Mapped[str] = mapped_column(
        String,
        ForeignKey(StaffEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    date: Mapped[DateTime] = mapped_column(DateTime, nullable=False, primary_key=True)
    staff = relationship(
        "StaffEntity",
        backref=backref(
            name=AWARD_COLLECTION_NAME,
            lazy="noload",
            cascade="all, delete-orphan",
            order_by="StaffAwardAssociation.date",
        ),
    )

    def __init__(self, staff, award, date: datetime):
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
