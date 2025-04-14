from sqlalchemy import Column, String, ForeignKey, Integer, ARRAY
from sqlalchemy.orm import relationship

from football_data_manager.common.repositories.grounds.ground_entity import GroundEntity
from football_data_manager.common.repositories.pulselive_entity import PulseliveEntity
from football_data_manager.common.repositories.seasons.season_entity import SeasonEntity
from football_data_manager.common.repositories.teams.team_entity import TeamEntity
from football_data_manager.common.utils.class_helper.class_property import classproperty


class TeamStatEntity(PulseliveEntity):
    """
    Team statistics entity model.
    :param id: Team statistics ID.
    :param away_matches: Away matches played.
    :param away_matches_drawn: Away matches drawn.
    :param away_matches_lost: Away matches lost.
    :param away_matches_won: Away matches won.
    :param away_goals_against: Away goals against.
    :param away_goals_for: Away goals for.
    :param away_goals_difference: Away goal difference.
    :param away_points: Away points.
    :param away_positions: Away match standing position.
    :param ground_id: The home ground ID.
    :param ground: The home ground entity.
    :param home_matches: Home matches played.
    :param home_matches_drawn: Home matches drawn.
    :param home_matches_lost: Home matches lost.
    :param home_matches_won: Home matches won.
    :param home_goals_against: Home goals against.
    :param home_goals_for: Home goals for.
    :param home_goals_difference: Home goal difference.
    :param home_points: Home points.
    :param home_positions: Home match standing position.
    :param overall_matches: Overall matches played.
    :param overall_matches_drawn: Overall matches drawn.
    :param overall_matches_lost: Overall matches lost.
    :param overall_matches_won: Overall matches won.
    :param overall_goals_against: Overall goals against.
    :param overall_goals_for: Overall goals for.
    :param overall_goals_difference: Overall goal difference.
    :param overall_points: Overall points.
    :param overall_position: Standing position.
    :param season_id: Season ID.
    :param season: Season entity.
    :param team_id: Team ID.
    :param team: Team entity.
    """

    __tablename__ = "team_stats"

    away_cumulative_points = Column(ARRAY(Integer))
    away_fixtures = Column(ARRAY(String))
    away_goals_against = Column(Integer)
    away_goals_for = Column(Integer)
    away_goals_difference = Column(Integer)
    away_matches = Column(Integer)
    away_matches_drawn = Column(Integer)
    away_matches_lost = Column(Integer)
    away_matches_won = Column(Integer)
    away_points = Column(Integer)
    away_positions = Column(Integer, nullable=True)
    ground_id = Column(String, ForeignKey(GroundEntity.id), nullable=True)
    ground = relationship(GroundEntity, lazy="joined", foreign_keys=[ground_id])
    home_cumulative_points = Column(ARRAY(Integer))
    home_fixtures = Column(ARRAY(String))
    home_goals_against = Column(Integer)
    home_goals_for = Column(Integer)
    home_goals_difference = Column(Integer)
    home_matches = Column(Integer)
    home_matches_drawn = Column(Integer)
    home_matches_lost = Column(Integer)
    home_matches_won = Column(Integer)
    home_points = Column(Integer)
    home_positions = Column(Integer, nullable=True)
    overall_cumulative_points = Column(ARRAY(Integer))
    overall_fixtures = Column(ARRAY(String))
    overall_goals_against = Column(Integer)
    overall_goals_for = Column(Integer)
    overall_goals_difference = Column(Integer)
    overall_matches = Column(Integer)
    overall_matches_drawn = Column(Integer)
    overall_matches_lost = Column(Integer)
    overall_matches_won = Column(Integer)
    overall_points = Column(Integer)
    overall_position = Column(Integer)
    season_id = Column(String, ForeignKey(SeasonEntity.id), nullable=False)
    season = relationship(SeasonEntity, lazy="joined", foreign_keys=[season_id])
    team_id = Column(String, ForeignKey(TeamEntity.id), nullable=False)
    team = relationship(TeamEntity, lazy="joined", foreign_keys=[team_id])

    @classproperty
    def entity_type(cls) -> str:
        """
        Get the prefix of the entity.
        :return: Entity prefix.
        """
        return "TEAM_STAT"
