from datetime import datetime

from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship

from football_data_manager.common.old_repositories.grounds.ground_entity import (
    GroundEntity,
)
from football_data_manager.common.old_repositories.pulselive_entity import (
    PulseliveEntity,
)
from football_data_manager.common.old_repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.old_repositories.teams.team_entity import TeamEntity


class FixtureEntity(PulseliveEntity):
    """
    Fixture entity model.
    :ivar id: Unique identifier for the entity.
    :ivar away_team_id: Away team ID associated with the fixture.
    :ivar ground_id: Ground ID associated with the fixture.
    :ivar home_team_id: Home team ID associated with the fixture.
    :ivar season_id: Season ID associated with the fixture.
    :ivar source: Source of the entity data, set to PULSELIVE.
    :param away_team: Away team entity associated with the fixture.
    :param away_team_score: Away team score.
    :param attendance: Attendance of the game.
    :param clock: Game clock.
    :param game_week: Game week number.
    :param ground: Ground entity associated with the fixture.
    :param home_team: Home team entity associated with the fixture.
    :param home_team_score: Home team score.
    :param neutral_ground: Neutral ground status.
    :param kickoff_time: Game kickoff time.
    :param season: Season entity associated with the fixture.
    :param source_id: Unique identifier from the source.
    """

    __tablename__ = "fixtures"

    away_team_id = Column(String, ForeignKey(TeamEntity.id), nullable=False)
    away_team = relationship(TeamEntity, lazy="joined", foreign_keys=away_team_id)
    away_team_score = Column(Integer, nullable=True)
    attendance = Column(Integer, nullable=True)
    clock = Column(Integer, nullable=True)
    game_week = Column(Integer, nullable=False)
    ground_id = Column(String, ForeignKey(GroundEntity.id), nullable=True)
    ground = relationship(GroundEntity, lazy="joined", foreign_keys=ground_id)
    home_team_id = Column(String, ForeignKey(TeamEntity.id), nullable=False)
    home_team = relationship(TeamEntity, lazy="joined", foreign_keys=home_team_id)
    home_team_score = Column(Integer, nullable=True)
    neutral_ground = Column(Boolean, nullable=False)
    kickoff_time = Column(DateTime, nullable=False)
    season_id = Column(String, ForeignKey(SeasonEntity.id), nullable=False)
    season = relationship(SeasonEntity, lazy="joined", foreign_keys=season_id)

    def __init__(
        self,
        away_team: TeamEntity,
        game_week: int,
        home_team: TeamEntity,
        neutral_ground: bool,
        kickoff_time: datetime,
        season: SeasonEntity,
        source_id: str,
        away_team_score: int | None = None,
        attendance: int | None = None,
        clock: int | None = None,
        ground: GroundEntity | None = None,
        home_team_score: int | None = None,
    ):
        super().__init__(source_id=source_id)
        self.away_team_id = away_team.id
        self.game_week = game_week
        self.home_team_id = home_team.id
        self.neutral_ground = neutral_ground
        self.kickoff_time = kickoff_time
        self.season_id = season.id
        self.away_team_score = away_team_score
        self.attendance = attendance
        self.clock = clock
        self.ground_id = ground.id if ground else None
        self.home_team_score = home_team_score

    @property
    def is_home_won(self) -> bool | None:
        """
        Check if the home team won the fixture.
        :return: True if home team won, False if away team won, None if scores are not available.
        """
        if self.home_team_score is None or self.away_team_score is None:
            return None
        else:
            return self.home_team_score > self.away_team_score

    @property
    def is_away_won(self) -> bool | None:
        """
        Check if the away team won the fixture.
        :return: True if away team won, False if home team won, None if scores are not available.
        """
        if self.away_team_score is None or self.home_team_score is None:
            return None
        else:
            return self.away_team_score > self.home_team_score

    @property
    def is_drawn(self) -> bool | None:
        """
        Check if the fixture ended in a draw.
        :return: True if the fixture ended in a draw, False otherwise, None if scores are not available.
        """
        if self.home_team_score is None or self.away_team_score is None:
            return None
        else:
            return self.home_team_score == self.away_team_score

    @property
    def is_home_lost(self) -> bool | None:
        """
        Check if the home team lost the fixture.
        :return: True if home team lost, False if away team lost, None if scores are not available.
        """
        if self.is_home_won is None:
            return None
        else:
            return not self.is_home_won and not self.is_drawn

    @property
    def is_away_lost(self) -> bool | None:
        """
        Check if the away team lost the fixture.
        :return: True if away team lost, False if home team lost, None if scores are not available.
        """
        if self.is_away_won is None:
            return None
        else:
            return not self.is_away_won and not self.is_drawn

    @property
    def away_point(self) -> int | None:
        """
        Get the away team point.
        :return: Away team point.
        """
        if self.is_away_won:
            return 3
        elif self.is_drawn:
            return 1
        elif self.is_away_lost:
            return 0
        else:
            return None

    @property
    def home_point(self) -> int | None:
        """
        Get the home team point.
        :return: Home team point.
        """
        if self.is_home_won:
            return 3
        elif self.is_drawn:
            return 1
        elif self.is_home_lost:
            return 0
        else:
            return None
