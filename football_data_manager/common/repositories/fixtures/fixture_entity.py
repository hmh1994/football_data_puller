from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    Integer,
    DateTime,
    Boolean,
    Index,
    desc,
)

from football_data_manager.common.repositories.constants import FIXTURES_TABLE_NAME
from football_data_manager.common.repositories.grounds.ground_entity import (
    GroundEntity,
)
from football_data_manager.common.repositories.pulselive_entity import (
    PulseliveEntity,
)
from football_data_manager.common.repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.repositories.teams.team_entity import TeamEntity


class FixtureEntity(PulseliveEntity):
    """
    Entity model for football fixtures (matches) with scheduling and team information.

    Represents scheduled football matches with teams, venue, timing, and game week details.
    Extends PulseliveEntity to inherit source tracking functionality.

    :ivar id: Unique identifier for the entity
    :ivar away_team_id: Foreign key to away team entity
    :ivar game_week: Game week number in the season
    :ivar ground_id: Foreign key to ground/venue entity (optional)
    :ivar home_team_id: Foreign key to home team entity
    :ivar neutral_ground: Boolean indicating if match is at neutral venue
    :ivar kickoff_time: Scheduled kickoff time for the match
    :ivar season_id: Foreign key to season entity
    :ivar source: Source of the entity data, set to PULSELIVE
    :ivar source_id: Unique identifier from the source system
    :ivar created_at: Entity creation timestamp
    :ivar updated_at: Last modification timestamp
    """

    __tablename__ = FIXTURES_TABLE_NAME

    away_team_id = Column(
        String,
        ForeignKey(TeamEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
    )
    game_week = Column(Integer, nullable=False)
    ground_id = Column(
        String,
        ForeignKey(GroundEntity.id, ondelete="SET NULL", onupdate="RESTRICT"),
        nullable=True,
    )
    home_team_id = Column(
        String,
        ForeignKey(TeamEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
    )
    neutral_ground = Column(Boolean, nullable=False)
    kickoff_time = Column(DateTime, nullable=False)
    season_id = Column(
        String,
        ForeignKey(SeasonEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_fixtures_away_team", away_team_id),
        Index("ix_fixtures_away_team_season", away_team_id, season_id),
        Index("ix_fixtures_home_team", home_team_id),
        Index("ix_fixtures_home_team_season", home_team_id, season_id),
        Index("ix_fixtures_kickoff_time_desc", desc(kickoff_time)),
    )

    def __init__(
        self,
        away_team: TeamEntity,
        game_week: int,
        home_team: TeamEntity,
        neutral_ground: bool,
        kickoff_time: datetime,
        season: SeasonEntity,
        source_id: str,
        ground: GroundEntity | None = None,
    ):
        """
        Initialize a new fixture entity.

        :param away_team: Away team entity for the match
        :param game_week: Game week number in the season
        :param home_team: Home team entity for the match
        :param neutral_ground: Boolean indicating if match is at neutral venue
        :param kickoff_time: Scheduled kickoff time for the match
        :param season: Season entity in which the fixture is scheduled
        :param source_id: Unique identifier from the source system
        :param ground: Ground/venue entity for the match (optional)
        """
        super().__init__(source_id=source_id)
        self.away_team_id = away_team.id
        self.game_week = game_week
        self.home_team_id = home_team.id
        self.neutral_ground = neutral_ground
        self.kickoff_time = kickoff_time
        self.season_id = season.id
        self.ground_id = ground.id if ground else None
