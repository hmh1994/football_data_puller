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
