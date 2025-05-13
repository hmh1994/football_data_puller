from sqlalchemy import Column, String, ARRAY, DateTime

from football_data_manager.common.repositories.base_entity import BaseEntity
from football_data_manager.common.utils.class_helper.class_property import classproperty


class NewsEntity(BaseEntity):
    __tablename__ = "news"
    author_en = Column(ARRAY(String))
    author_kr = Column(ARRAY(String))
    content_en = Column(String)
    content_kr = Column(String)
    publish_date = Column(DateTime)
    url = Column(String)
    source = Column(String)
    teams = Column(ARRAY(String))
    thumbnail_url = Column(String)
    title_en = Column(String)
    title_kr = Column(String)
    type = Column(String)

    @classproperty
    def entity_type(cls) -> str:
        """
        Get the prefix of the entity.
        :return: Entity prefix
        """
        return f"NEWS"

    @classproperty
    def the_athletic_prefix(cls) -> str:
        """
        Get the prefix of the entity.
        :return: Entity prefix
        """
        return f"THEATHLETIC_{cls.entity_type}"

    @classmethod
    def get_the_athletic_id(cls, api_id: str, index: int) -> str:
        """
        Get the ID of the entity.
        :param api_id: The ID of the entity from the API.
        :param index: The index of the entity.
        :return: Entity ID.
        """
        assert cls.the_athletic_prefix is not None, "Entity prefix is not set."
        return f"{cls.the_athletic_prefix}_{api_id}_{index}"

    @property
    def the_athletic_id(self) -> str:
        """
        Get the API ID of the entity.
        :return: API ID.
        """
        assert self.the_athletic_prefix is not None, "Entity prefix is not set."
        return self.id.removeprefix(f"{self.the_athletic_prefix}_")
