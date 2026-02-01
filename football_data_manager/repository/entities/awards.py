from hashlib import md5

from sqlalchemy import String, Enum
from sqlalchemy.orm import Mapped, mapped_column

from football_data_manager.common.enums.award_type_enum import AwardTypeEnum
from football_data_manager.repository.entities.base import PulseliveEntity

AWARDS_TABLE_NAME = "awards"


class AwardEntity(PulseliveEntity):
    """
    Entity model for football awards with multilingual information.

    :ivar type: Award type enum value (e.g., POTM, MOTM, GOTM)
    :ivar description_en: Award type description in English
    :ivar description_kr: Award type description in Korean
    :ivar icon_url: URL of the award type icon
    :ivar name_en: Award type name in English
    :ivar name_kr: Award type name in Korean
    """

    __tablename__ = AWARDS_TABLE_NAME

    description_en: Mapped[str | None] = mapped_column(String, nullable=True)
    description_kr: Mapped[str | None] = mapped_column(String, nullable=True)
    icon_url: Mapped[str | None] = mapped_column(String, nullable=True)
    name_en: Mapped[str | None] = mapped_column(String, nullable=True)
    name_kr: Mapped[str | None] = mapped_column(String, nullable=True)
    type: Mapped[AwardTypeEnum] = mapped_column(Enum(AwardTypeEnum), nullable=False)

    def __init__(
        self,
        _type: AwardTypeEnum,
        name_en: str | None = None,
        name_kr: str | None = None,
        description_en: str | None = None,
        description_kr: str | None = None,
        icon_url: str | None = None,
    ):
        """
        Initialize a new award entity.

        :param _type: Award type enum value
        :param name_en: Award type name in English (optional)
        :param name_kr: Award type name in Korean (optional)
        :param description_en: Award type description in English (optional)
        :param description_kr: Award type description in Korean (optional)
        :param icon_url: URL of the award type icon (optional)
        """
        super().__init__(source_id=self.get_source_id(_type))
        self.type = _type
        self.name_en = name_en
        self.name_kr = name_kr
        self.description_en = description_en
        self.description_kr = description_kr
        self.icon_url = icon_url

    @staticmethod
    def get_source_id(_type: AwardTypeEnum) -> str:
        """
        Generate a unique source ID for the award based on its type.

        :param _type: The award type enum value
        :returns: Unique source ID as a string
        """
        type_value = _type.value.encode("utf-8")
        hashed_type = md5(type_value).hexdigest()
        return str(int(hashed_type, 16) % 2**16)
