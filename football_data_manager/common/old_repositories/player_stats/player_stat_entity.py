from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship

from football_data_manager.common.old_repositories.players.player_entity import (
    PlayerEntity,
)
from football_data_manager.common.old_repositories.pulselive_entity import (
    PulseliveEntity,
)
from football_data_manager.common.old_repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.old_repositories.teams.team_entity import TeamEntity


class PlayerStatEntity(PulseliveEntity):
    """
    Player statistics entity model.
    :ivar id: Unique identifier for the player stat.
    :ivar player_id: Player ID associated with the stats.
    :ivar season_id: Season ID associated with the stats.
    :ivar team_id: Team ID associated with the stats.
    :ivar source: Source of the entity data, set to PULSELIVE.
    :ivar source_id: Unique identifier from the source.
    :param appearances: Number of appearances.
    :param assists: Number of assists.
    :param clean_sheets: Number of clean sheets.
    :param goals: Number of goals scored.
    :param goals_conceded: Number of goals conceded.
    :param key_passes: Number of key passes.
    :param number: Player's jersey number.
    :param player: Player entity associated with the stats.
    :param saves: Number of saves made.
    :param season: Season entity associated with the stats.
    :param shots: Number of shots taken.
    :param tackles: Number of tackles made.
    :param team: Team entity associated with the stats.
    """

    __tablename__ = "player_stats"

    appearances = Column(Integer, nullable=False)
    assists = Column(Integer, nullable=False)
    clean_sheets = Column(Integer, nullable=False)
    goals = Column(Integer, nullable=False)
    goals_conceded = Column(Integer, nullable=False)
    key_passes = Column(Integer, nullable=False)
    number = Column(Integer, nullable=False)
    player_id = Column(String, ForeignKey(PlayerEntity.id), nullable=False)
    player = relationship(PlayerEntity, lazy="joined", foreign_keys=player_id)
    saves = Column(Integer, nullable=False)
    season_id = Column(String, ForeignKey(SeasonEntity.id), nullable=False)
    season = relationship(SeasonEntity, lazy="joined", foreign_keys=season_id)
    shots = Column(Integer, nullable=False)
    tackles = Column(Integer, nullable=False)
    team_id = Column(String, ForeignKey(TeamEntity.id), nullable=False)
    team = relationship(TeamEntity, lazy="joined", foreign_keys=team_id)

    def __init__(
        self,
        appearances: int,
        assists: int,
        clean_sheets: int,
        goals: int,
        goals_conceded: int,
        key_passes: int,
        number: int,
        player: PlayerEntity,
        saves: int,
        season: SeasonEntity,
        shots: int,
        tackles: int,
        team: TeamEntity,
    ):
        super().__init__(source_id=self.get_source_id(season, player))
        self.appearances = appearances
        self.assists = assists
        self.award_ids = []
        self.awards = []
        self.clean_sheets = clean_sheets
        self.goals = goals
        self.goals_conceded = goals_conceded
        self.key_passes = key_passes
        self.number = number
        self.player_id = player.id
        self.saves = saves
        self.season_id = season.id
        self.shots = shots
        self.tackles = tackles
        self.team_id = team.id

    @staticmethod
    def get_source_id(season: SeasonEntity, player: PlayerEntity) -> str:
        """
        Generates a unique source ID for the player stat entity based on the season and player.
        :param season: Season entity.
        :param player: Player entity.
        :return: Unique source ID.
        """
        return f"{season.source_id}_{player.source_id}"
