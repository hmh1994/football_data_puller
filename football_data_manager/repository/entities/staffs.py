from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from football_data_manager.repository.entities.base import PulseliveEntity

STAFFS_TABLE_NAME = "staffs"


class StaffEntity(PulseliveEntity):
    """
    Entity model for football coaching staff and management personnel.

    :ivar display_name_en: Staff member's display name in English
    :ivar display_name_kr: Staff member's display name in Korean
    :ivar full_name: Staff member's full legal name
    """

    __tablename__ = STAFFS_TABLE_NAME

    display_name_en: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    display_name_kr: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)

    def __init__(
        self, display_name_en: str, display_name_kr: str, full_name: str, source_id: str
    ) -> None:
        """
        Initialize a new staff entity.

        :param display_name_en: Staff member's display name in English
        :param display_name_kr: Staff member's display name in Korean
        :param full_name: Staff member's full legal name
        :param source_id: Unique identifier from the source system
        """
        super().__init__(source_id=source_id)
        self.display_name_en = display_name_en
        self.display_name_kr = display_name_kr
        self.full_name = full_name
        self.award_associations = []
