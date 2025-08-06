from sqlalchemy import Column, String, ForeignKey, Integer

from football_data_manager.common.repositories.constants import (
    PLAYER_STATS_TABLE_NAME,
)
from football_data_manager.common.repositories.players.player_entity import (
    PlayerEntity,
)
from football_data_manager.common.repositories.pulselive_entity import (
    PulseliveEntity,
)
from football_data_manager.common.repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.repositories.teams.team_entity import TeamEntity


class PlayerStatEntity(PulseliveEntity):
    """
    Entity model for player statistics with performance metrics and awards.

    Represents comprehensive player performance statistics for a specific season
    and team, including goals, assists, appearances, and award associations.
    Extends PulseliveEntity to inherit source tracking functionality.

    :ivar id: Unique identifier for the player stat
    :ivar appearances: Number of appearances in matches
    :ivar assists: Number of assists provided
    :ivar award_associations: List of awards received during the season
    :ivar clean_sheets: Number of clean sheets (for goalkeepers)
    :ivar goals: Number of goals scored
    :ivar goals_conceded: Number of goals conceded (for goalkeepers)
    :ivar key_passes: Number of key passes made
    :ivar number: Player's jersey number for the season
    :ivar player_id: Foreign key to the associated player
    :ivar saves: Number of saves made (for goalkeepers)
    :ivar season_id: Foreign key to the associated season
    :ivar shots: Number of shots taken
    :ivar tackles: Number of tackles made
    :ivar team_id: Foreign key to the associated team
    :ivar source: Source of the entity data, set to PULSELIVE
    :ivar source_id: Unique identifier from the source
    :ivar created_at: Entity creation timestamp
    :ivar updated_at: Last modification timestamp
    """

    __tablename__ = PLAYER_STATS_TABLE_NAME

    appearances = Column(Integer, nullable=False)
    assists = Column(Integer, nullable=False)
    clean_sheets = Column(Integer, nullable=False)
    goals = Column(Integer, nullable=False)
    goals_conceded = Column(Integer, nullable=False)
    key_passes = Column(Integer, nullable=False)
    number = Column(Integer, nullable=False)
    player_id = Column(
        String,
        ForeignKey(PlayerEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
    )
    saves = Column(Integer, nullable=False)
    season_id = Column(
        String,
        ForeignKey(SeasonEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
    )
    shots = Column(Integer, nullable=False)
    tackles = Column(Integer, nullable=False)
    team_id = Column(
        String,
        ForeignKey(TeamEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
    )

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
        """
        Initialize a new player stat entity.

        :param appearances: Number of appearances in matches
        :param assists: Number of assists provided
        :param clean_sheets: Number of clean sheets (for goalkeepers)
        :param goals: Number of goals scored
        :param goals_conceded: Number of goals conceded (for goalkeepers)
        :param key_passes: Number of key passes made
        :param number: Player's jersey number for the season
        :param player: Player entity associated with the statistics
        :param saves: Number of saves made (for goalkeepers)
        :param season: Season entity for which statistics are recorded
        :param shots: Number of shots taken
        :param tackles: Number of tackles made
        :param team: Team entity the player played for
        """
        super().__init__(source_id=self.get_source_id(season, player))
        self.appearances = appearances
        self.assists = assists
        self.award_associations = []
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
        Generate a unique source ID for the player stat entity.

        :param season: Season entity for which statistics are recorded
        :param player: Player entity associated with the statistics
        :returns: Unique source ID combining season and player identifiers
        """
        return f"{season.source_id}_{player.source_id}"
