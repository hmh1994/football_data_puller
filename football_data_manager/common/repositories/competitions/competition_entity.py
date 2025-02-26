from sqlalchemy import Column, String

from football_data_manager.common.repositories import Base


class CompetitionEntity(Base):
    """
    Competition entity model.
    :param id: Competition ID.
    :param abbreviation: Competition abbreviation.
    :param description_en: Competition description in English.
    :param description_kr: Competition description in Korean.
    :param icon_url: Competition icon URL.
    :param name_en: Competition name in English.
    :param name_kr: Competition name in Korean.
    """

    __tablename__ = "competitions"

    id = Column(String, primary_key=True)
    abbreviation = Column(String)
    description_en = Column(String, nullable=True)
    description_kr = Column(String, nullable=True)
    icon_url = Column(String, nullable=True)
    name_en = Column(String)
    name_kr = Column(String, nullable=True)

    @staticmethod
    def get_id(pulselive_id: int) -> str:
        """
        Get the ID of the competition.
        :param pulselive_id: Pulselive ID.
        :return: Competition ID.
        """
        return f"PULSELIVE_COMPETITION_{pulselive_id}"

    @property
    def pulselive_id(self) -> int:
        """
        Get the Pulselive ID of the competition.
        :return: Pulselive ID.
        """
        return int(self.id.removeprefix("PULSELIVE_COMPETITION_"))
