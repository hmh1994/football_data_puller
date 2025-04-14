from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship

from football_data_manager.common.repositories import Base
from football_data_manager.common.repositories.grounds.ground_entity import GroundEntity
from football_data_manager.common.repositories.seasons.season_entity import SeasonEntity
from football_data_manager.common.repositories.teams.team_entity import TeamEntity


class FixtureEntity(Base):
    """
    Fixture entity model.
    :param id: Fixture ID.
    :param away_team_id: Away team ID.
    :param away_team: Away team entity.
    :param away_team_score: Away team score.
    :param attendance: Attendance of the game.
    :param clock: Game clock.
    :param game_week: Game week number.
    :param ground_id: Ground ID.
    :param ground: Ground entity.
    :param home_team_id: Home team ID.
    :param home_team: Home team entity.
    :param home_team_score: Home team score.
    :param neutral_ground: Neutral ground status.
    :param kickoff_time: Game kickoff time.
    :param season_id: Season ID.
    :param season: Season entity.
    """

    __tablename__ = "fixtures"

    id = Column(String, primary_key=True)
    away_team_id = Column(String, ForeignKey(TeamEntity.id))
    away_team = relationship(TeamEntity, lazy="joined", foreign_keys=[away_team_id])
    away_team_score = Column(Integer, nullable=True)
    attendance = Column(Integer, nullable=True)
    clock = Column(Integer, nullable=True)
    game_week = Column(Integer)
    ground_id = Column(String, ForeignKey(GroundEntity.id), nullable=True)
    ground = relationship(GroundEntity, lazy="joined", foreign_keys=[ground_id])
    home_team_id = Column(String, ForeignKey(TeamEntity.id))
    home_team = relationship(TeamEntity, lazy="joined", foreign_keys=[home_team_id])
    home_team_score = Column(Integer, nullable=True)
    neutral_ground = Column(Boolean)
    kickoff_time = Column(DateTime)
    season_id = Column(String, ForeignKey(SeasonEntity.id))
    season = relationship(SeasonEntity, lazy="joined", foreign_keys=[season_id])

    @staticmethod
    def get_id(pulselive_id: int) -> str:
        """
        Get the ID of the fixture.
        :param pulselive_id: Pulselive ID.
        :return: Fixture ID.
        """
        return f"PULSELIVE_FIXTURE_{pulselive_id}"

    @property
    def pulselive_id(self) -> int:
        """
        Get the Pulselive ID of the fixture.
        :return: Pulselive ID.
        """
        return int(self.id.removeprefix("PULSELIVE_FIXTURE_"))

    @property
    def away_point(self) -> int | None:
        """
        Get the away team point.
        :return: Away team point.
        """
        if self.away_team_score is None or self.home_team_score is None:
            return None
        elif self.away_team_score > self.home_team_score:
            return 3
        elif self.away_team_score == self.home_team_score:
            return 1
        else:
            return 0

    @property
    def home_point(self) -> int | None:
        """
        Get the home team point.
        :return: Home team point.
        """
        if self.home_team_score is None or self.away_team_score is None:
            return None
        elif self.home_team_score > self.away_team_score:
            return 3
        elif self.home_team_score == self.away_team_score:
            return 1
        else:
            return 0
