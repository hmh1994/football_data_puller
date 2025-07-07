from typing import Self

from sqlalchemy import Column, String
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship

from football_data_manager.common.new_repositories.pulselive_entity import (
    PulseliveEntity,
)
from football_data_manager.common.new_repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.new_repositories.teams.team_championship_association import (
    TeamChampionshipAssociation,
)
from football_data_manager.common.services.db.db_service import DbService


class TeamEntity(PulseliveEntity):
    """
    Team entity model.
    :ivar id: Unique identifier for the entity.
    :ivar championship_seasons: List of championship seasons entities related to the team.
    :ivar source: Source of the entity data, set to PULSELIVE.
    :param abbreviation: Team abbreviation.
    :param icon_url: Team icon URL.
    :param name_en: Team name in English.
    :param name_kr: Team name in Korean.
    :param short_name_en: Team short name in English.
    :param short_name_kr: Team short name in Korean.
    :param source_id: Unique identifier from the source.
    """

    __tablename__ = "teams_new"

    abbreviation = Column(String, nullable=False)
    championship_season_associations = relationship(
        TeamChampionshipAssociation,
        back_populates="team",
        cascade="all, delete-orphan",
        single_parent=True,
        lazy="joined",
        collection_class=ordering_list("date_end"),
        order_by=TeamChampionshipAssociation.date_end,
    )
    championship_seasons = relationship(
        SeasonEntity,
        secondary=TeamChampionshipAssociation.__table__,
        viewonly=True,
        lazy="select",
    )
    icon_url = Column(String, nullable=True)
    name_en = Column(String, nullable=False)
    name_kr = Column(String, nullable=False)
    short_name_en = Column(String, nullable=False)
    short_name_kr = Column(String, nullable=False)

    def __init__(
        self,
        abbreviation: str,
        icon_url: str,
        name_en: str,
        name_kr: str,
        short_name_en: str,
        short_name_kr: str,
        source_id: str,
    ) -> None:
        super().__init__(source_id=source_id)
        self.abbreviation = abbreviation
        self.icon_url = icon_url
        self.name_en = name_en
        self.name_kr = name_kr
        self.short_name_en = short_name_en
        self.short_name_kr = short_name_kr

    async def update_championship_season(
        self, db_service: DbService, season: SeasonEntity
    ) -> Self:
        """
        Apply a championship season to the team.
        :param db_service: Database service for saving the association.
        :param season: Season entity to apply.
        :return: The updated team entity.
        """
        async with db_service.create_db_session() as session:
            merged_entity = await session.merge(self)
            await session.refresh(merged_entity, ["championship_season_associations"])
        if all(
            association.season_id != season.id
            for association in merged_entity.championship_season_associations
        ):
            association = TeamChampionshipAssociation(
                team_id=self.id, season_id=season.id, date_end=season.date_end
            )
            merged_entity.championship_season_associations.append(association)
        return merged_entity
