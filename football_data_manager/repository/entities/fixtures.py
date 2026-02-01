from datetime import datetime

from sqlalchemy import String, ForeignKey, Integer, DateTime, Index, desc
from sqlalchemy.orm import Mapped, mapped_column

from football_data_manager.repository.entities.base import PulseliveEntity
from football_data_manager.repository.entities.grounds import GroundEntity
from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.entities.teams import TeamEntity

FIXTURES_TABLE_NAME = "fixtures"


class FixtureEntity(PulseliveEntity):
    """
    Entity model for football fixtures (scheduled matches).

    :ivar away_team_id: Foreign key to away team entity
    :ivar game_week: Game week number in the season
    :ivar ground_id: Foreign key to ground/venue entity (optional)
    :ivar home_team_id: Foreign key to home team entity
    :ivar kickoff_time: Scheduled kickoff time for the match
    :ivar season_id: Foreign key to season entity
    """

    __tablename__ = FIXTURES_TABLE_NAME

    away_team_id: Mapped[str] = mapped_column(
        String,
        ForeignKey(TeamEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
    )
    game_week: Mapped[int] = mapped_column(Integer, nullable=False)
    ground_id: Mapped[str | None] = mapped_column(
        String,
        ForeignKey(GroundEntity.id, ondelete="SET NULL", onupdate="RESTRICT"),
        nullable=True,
    )
    home_team_id: Mapped[str] = mapped_column(
        String,
        ForeignKey(TeamEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
    )
    kickoff_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    season_id: Mapped[str] = mapped_column(
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
        :param kickoff_time: Scheduled kickoff time for the match
        :param season: Season entity
        :param source_id: Unique identifier from the source system
        :param ground: Ground/venue entity for the match (optional)
        """
        super().__init__(source_id=source_id)
        self.away_team_id = away_team.id
        self.game_week = game_week
        self.home_team_id = home_team.id
        self.kickoff_time = kickoff_time
        self.season_id = season.id
        self.ground_id = ground.id if ground else None
