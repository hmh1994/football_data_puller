from sqlalchemy import Column, String, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship

from football_data_manager.common.repositories import Base
from football_data_manager.common.repositories.seasons.season_entity import SeasonEntity
from football_data_manager.common.repositories.teams.team_entity import TeamEntity


class StandingEntity(Base):
    """
    Standing entity model.
    :param id: Standing ID.
    :param away_matches: Away matches played.
    :param away_matches_drawn: Away matches drawn.
    :param away_matches_lost: Away matches lost.
    :param away_matches_won: Away matches won.
    :param away_goals_against: Away goals against.
    :param away_goals_for: Away goals for.
    :param away_goal_difference: Away goal difference.
    :param away_points: Away points.
    :param away_positions: Away match standing position.
    :param game_week: Game week number.
    :param home_matches: Home matches played.
    :param home_matches_drawn: Home matches drawn.
    :param home_matches_lost: Home matches lost.
    :param home_matches_won: Home matches won.
    :param home_goals_against: Home goals against.
    :param home_goals_for: Home goals for.
    :param home_goal_difference: Home goal difference.
    :param home_points: Home points.
    :param home_positions: Home match standing position.
    :param latest: Latest standing status.
    :param last_five_matches: Last five matches `^[WDL]{5}$`.
    :param overall_matches: Overall matches played.
    :param overall_matches_drawn: Overall matches drawn.
    :param overall_matches_lost: Overall matches lost.
    :param overall_matches_won: Overall matches won.
    :param overall_goals_against: Overall goals against.
    :param overall_goals_for: Overall goals for.
    :param overall_goal_difference: Overall goal difference.
    :param overall_points: Overall points.
    :param overall_position: Standing position.
    :param season_id: Season ID.
    :param season: Season entity.
    :param team_id: Team ID.
    :param team: Team entity.
    """

    __tablename__ = "standings"

    id = Column(String, primary_key=True)
    away_matches = Column(Integer)
    away_matches_drawn = Column(Integer)
    away_matches_lost = Column(Integer)
    away_matches_won = Column(Integer)
    away_goals_against = Column(Integer)
    away_goals_for = Column(Integer)
    away_goal_difference = Column(Integer)
    away_points = Column(Integer)
    away_positions = Column(Integer)
    game_week = Column(Integer)
    home_matches = Column(Integer)
    home_matches_drawn = Column(Integer)
    home_matches_lost = Column(Integer)
    home_matches_won = Column(Integer)
    home_goals_against = Column(Integer)
    home_goals_for = Column(Integer)
    home_goal_difference = Column(Integer)
    home_points = Column(Integer)
    home_positions = Column(Integer)
    latest = Column(Boolean)
    last_five_matches = Column(String)
    overall_matches = Column(Integer)
    overall_matches_drawn = Column(Integer)
    overall_matches_lost = Column(Integer)
    overall_matches_won = Column(Integer)
    overall_goals_against = Column(Integer)
    overall_goals_for = Column(Integer)
    overall_goal_difference = Column(Integer)
    overall_points = Column(Integer)
    overall_position = Column(Integer)
    season_id = Column(String, ForeignKey(SeasonEntity.id))
    season = relationship(SeasonEntity, lazy="joined", foreign_keys=[season_id])
    team_id = Column(String, ForeignKey(TeamEntity.id))
    team = relationship(TeamEntity, lazy="joined", foreign_keys=[team_id])
