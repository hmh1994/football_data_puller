from hashlib import md5

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from football_data_manager.repository.entities.base import PulseliveEntity

OFFICIALS_TABLE_NAME = "officials"


class OfficialEntity(PulseliveEntity):
    """
    Entity model for football officials (referees, assistants, VAR officials).

    :ivar display_name_en: Official's display name in English
    :ivar display_name_kr: Official's display name in Korean
    :ivar full_name: Official's full legal name
    """

    __tablename__ = OFFICIALS_TABLE_NAME

    display_name_en: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    display_name_kr: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)

    def __init__(self, display_name_en: str, display_name_kr: str, full_name: str):
        """
        Initialize a new official entity.

        :param display_name_en: Official's display name in English
        :param display_name_kr: Official's display name in Korean
        :param full_name: Official's full legal name
        """
        super().__init__(source_id=self.get_source_id(display_name_en))
        self.display_name_en = display_name_en
        self.display_name_kr = display_name_kr
        self.full_name = full_name

    @staticmethod
    def get_source_id(display_name_en: str) -> str:
        """
        Generate a unique source ID for the official.

        :param display_name_en: The displayed name of the official in English
        :returns: Unique source ID as a string
        """
        normal_name = display_name_en.encode("utf-8")
        hashed_name = md5(normal_name).hexdigest()
        return str(int(hashed_name, 16) % 2**16)
