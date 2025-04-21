from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship

from football_data_manager.common.repositories.players.player_entity import PlayerEntity
from football_data_manager.common.repositories.pulselive_entity import PulseliveEntity
from football_data_manager.common.repositories.seasons.season_entity import SeasonEntity
from football_data_manager.common.repositories.teams.team_entity import TeamEntity
from football_data_manager.common.utils.class_helper.class_property import classproperty


class PlayerStatEntity(PulseliveEntity):
    __tablename__ = "player_stats"

    appearances = Column(Integer)
    assists = Column(Integer)
    clean_sheets = Column(Integer)
    goals = Column(Integer)
    goals_conceded = Column(Integer)
    key_passes = Column(Integer)
    number = Column(Integer)
    player_id = Column(String, ForeignKey(PlayerEntity.id))
    player = relationship(PlayerEntity, lazy="joined", foreign_keys=[player_id])
    saves = Column(Integer)
    season_id = Column(String, ForeignKey(SeasonEntity.id))
    season = relationship(SeasonEntity, lazy="joined", foreign_keys=[season_id])
    shots = Column(Integer)
    tackles = Column(Integer)
    team_id = Column(String, ForeignKey(TeamEntity.id))
    team = relationship(TeamEntity, lazy="joined", foreign_keys=[team_id])

    @classproperty
    def entity_type(cls) -> str:
        """
        Get the prefix of the entity.
        :return: Entity prefix.
        """
        return "PLAYER_STAT"
