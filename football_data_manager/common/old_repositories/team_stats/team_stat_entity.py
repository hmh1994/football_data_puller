from typing import Self

from sqlalchemy import Column, String, ForeignKey, Integer, ARRAY
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


class TeamStatEntity(PulseliveEntity):
    """
    Team statistics entity model.
    :ivar id: Unique identifier for the team stat.
    :ivar away_matches: Away matches played.
    :ivar away_matches_drawn: Away matches drawn.
    :ivar away_matches_lost: Away matches lost.
    :ivar away_matches_won: Away matches won.
    :ivar away_goals_against: Away goals against.
    :ivar away_goals_for: Away goals for.
    :ivar away_goals_difference: Away goal difference.
    :ivar away_points: Away points.
    :ivar away_positions: Away match standing position.
    :ivar ground_id: Home ground ID associated with the stats.
    :ivar home_matches: Home matches played.
    :ivar home_matches_drawn: Home matches drawn.
    :ivar home_matches_lost: Home matches lost.
    :ivar home_matches_won: Home matches won.
    :ivar home_goals_against: Home goals against.
    :ivar home_goals_for: Home goals for.
    :ivar home_goals_difference: Home goal difference.
    :ivar home_points: Home points.
    :ivar home_positions: Home match standing position.
    :ivar overall_matches: Overall matches played.
    :ivar overall_matches_drawn: Overall matches drawn.
    :ivar overall_matches_lost: Overall matches lost.
    :ivar overall_matches_won: Overall matches won.
    :ivar overall_goals_against: Overall goals against.
    :ivar overall_goals_for: Overall goals for.
    :ivar overall_goals_difference: Overall goal difference.
    :ivar overall_points: Overall points.
    :ivar overall_position: Standing position.
    :ivar season: Season ID associated with the stats.
    :ivar source_id: Source of the entity data, set to PULSELIVE.
    :ivar team_id: Team ID associated with the stats.
    :param ground: Home ground entity associated with the team.
    :param season: Season entity associated with the stats.
    :param team: Team entity associated with the stats.
    """

    __tablename__ = "team_stats"

    away_cumulative_points = Column(ARRAY(Integer), nullable=False)
    away_fixtures = Column(ARRAY(String), nullable=False)
    away_goals_against = Column(Integer, nullable=False)
    away_goals_for = Column(Integer, nullable=False)
    away_goals_difference = Column(Integer, nullable=False)
    away_matches = Column(Integer, nullable=False)
    away_matches_drawn = Column(Integer, nullable=False)
    away_matches_lost = Column(Integer, nullable=False)
    away_matches_won = Column(Integer, nullable=False)
    away_points = Column(Integer, nullable=False)
    away_positions = Column(Integer, nullable=True)
    ground_id = Column(String, ForeignKey(GroundEntity.id), nullable=False)
    ground = relationship(GroundEntity, lazy="joined", foreign_keys=[ground_id])
    home_cumulative_points = Column(ARRAY(Integer), nullable=False)
    home_fixtures = Column(ARRAY(String), nullable=False)
    home_goals_against = Column(Integer, nullable=False)
    home_goals_for = Column(Integer, nullable=False)
    home_goals_difference = Column(Integer, nullable=False)
    home_matches = Column(Integer, nullable=False)
    home_matches_drawn = Column(Integer, nullable=False)
    home_matches_lost = Column(Integer, nullable=False)
    home_matches_won = Column(Integer, nullable=False)
    home_points = Column(Integer, nullable=False)
    home_positions = Column(Integer, nullable=True)
    overall_cumulative_points = Column(ARRAY(Integer), nullable=False)
    overall_fixtures = Column(ARRAY(String), nullable=False)
    overall_goals_against = Column(Integer, nullable=False)
    overall_goals_for = Column(Integer, nullable=False)
    overall_goals_difference = Column(Integer, nullable=False)
    overall_matches = Column(Integer, nullable=False)
    overall_matches_drawn = Column(Integer, nullable=False)
    overall_matches_lost = Column(Integer, nullable=False)
    overall_matches_won = Column(Integer, nullable=False)
    overall_points = Column(Integer, nullable=False)
    overall_position = Column(Integer, nullable=False)
    season_id = Column(String, ForeignKey(SeasonEntity.id), nullable=False)
    season = relationship(SeasonEntity, lazy="joined", foreign_keys=[season_id])
    team_id = Column(String, ForeignKey(TeamEntity.id), nullable=False)
    team = relationship(TeamEntity, lazy="joined", foreign_keys=[team_id])

    def __init__(
        self,
        ground: GroundEntity,
        season: SeasonEntity,
        source_id: str,
        team: TeamEntity,
    ) -> Self:
        super().__init__(source_id=source_id)
        self.away_cumulative_points = []
        self.away_fixtures = []
        self.away_goals_against = 0
        self.away_goals_for = 0
        self.away_goals_difference = 0
        self.away_matches = 0
        self.away_matches_drawn = 0
        self.away_matches_lost = 0
        self.away_matches_won = 0
        self.away_points = 0
        self.away_positions = None
        self.ground_id = ground.id
        self.home_cumulative_points = []
        self.home_fixtures = []
        self.home_goals_against = 0
        self.home_goals_for = 0
        self.home_goals_difference = 0
        self.home_matches = 0
        self.home_matches_drawn = 0
        self.home_matches_lost = 0
        self.home_matches_won = 0
        self.home_points = 0
        self.home_positions = None
        self.overall_cumulative_points = []
        self.overall_fixtures = []
        self.overall_goals_against = 0
        self.overall_goals_for = 0
        self.overall_goals_difference = 0
        self.overall_matches = 0
        self.overall_matches_drawn = 0
        self.overall_matches_lost = 0
        self.overall_matches_won = 0
        self.overall_points = 0
        self.overall_position = 0
        self.season_id = season.id
        self.team_id = team.id
