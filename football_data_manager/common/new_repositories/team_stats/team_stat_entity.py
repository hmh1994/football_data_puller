from typing import Self

from sqlalchemy import Column, String, ForeignKey, Integer, ARRAY
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from football_data_manager.common.new_repositories.constants import (
    TEAM_STATS_TABLE_NAME,
)
from football_data_manager.common.new_repositories.fixtures.fixture_entity import (
    FixtureEntity,
)
from football_data_manager.common.new_repositories.grounds.ground_entity import (
    GroundEntity,
)
from football_data_manager.common.new_repositories.pulselive_entity import (
    PulseliveEntity,
)
from football_data_manager.common.new_repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.new_repositories.team_stats.team_stat_away_fixture_association import (
    TeamStatAwayFixtureAssociation,
)
from football_data_manager.common.new_repositories.team_stats.team_stat_home_fixture_association import (
    TeamStatHomeFixtureAssociation,
)
from football_data_manager.common.new_repositories.team_stats.team_stat_overall_fixture_association import (
    TeamStatOverallFixtureAssociation,
)
from football_data_manager.common.new_repositories.teams.team_entity import TeamEntity
from football_data_manager.common.services.db.db_service import DbService
from football_data_manager.common.utils.type_helper.int_helper import compare_ints


class TeamStatEntity(PulseliveEntity):
    """
    Team statistics entity model.
    :ivar id: Unique identifier for the team stat.
    :ivar away_cumulative_points: Cumulative points in away matches.
    :ivar away_fixtures: List of fixture entities related to away matches.
    :ivar away_goals_against: Away goals against.
    :ivar away_goals_for: Away goals for.
    :ivar away_goals_difference: Away goal difference.
    :ivar away_matches: Away matches played.
    :ivar away_matches_drawn: Away matches drawn.
    :ivar away_matches_lost: Away matches lost.
    :ivar away_matches_won: Away matches won.
    :ivar away_points: Away points.
    :ivar away_position: Away match standing position.
    :ivar ground_id: Home ground ID associated with the stats.
    :ivar home_cumulative_points: Cumulative points in home matches.
    :ivar home_fixtures: List of fixture entities related to home matches.
    :ivar home_goals_against: Home goals against.
    :ivar home_goals_for: Home goals for.
    :ivar home_goals_difference: Home goal difference.
    :ivar home_matches: Home matches played.
    :ivar home_matches_drawn: Home matches drawn.
    :ivar home_matches_lost: Home matches lost.
    :ivar home_matches_won: Home matches won.
    :ivar home_points: Home points.
    :ivar home_position: Home match standing position.
    :ivar overall_cumulative_points: Cumulative points in overall matches.
    :ivar overall_fixtures: List of fixture entities related to overall matches.
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

    __tablename__ = TEAM_STATS_TABLE_NAME

    away_cumulative_points = Column(ARRAY(Integer), nullable=False)
    away_fixtures = association_proxy(
        target_collection=TeamStatAwayFixtureAssociation.FIXTURE_COLLECTION_NAME,
        attr=TeamStatAwayFixtureAssociation.FIXTURE_ATTRIBUTE_NAME,
        creator=lambda fixture: TeamStatAwayFixtureAssociation(  # type: ignore[arg-type]
            fixture=fixture, kickoff_time=fixture.kickoff_time  # type: ignore[arg-type]
        ),
    )
    away_goals_against = Column(Integer, nullable=False)
    away_goals_for = Column(Integer, nullable=False)
    away_goals_difference = Column(Integer, nullable=False)
    away_matches = Column(Integer, nullable=False)
    away_matches_drawn = Column(Integer, nullable=False)
    away_matches_lost = Column(Integer, nullable=False)
    away_matches_won = Column(Integer, nullable=False)
    away_points = Column(Integer, nullable=False)
    away_position = Column(Integer, nullable=True)
    ground_id = Column(String, ForeignKey(GroundEntity.id), nullable=False)
    ground = relationship(GroundEntity, lazy="selectin", foreign_keys=ground_id)
    home_cumulative_points = Column(ARRAY(Integer), nullable=False)
    home_fixtures = association_proxy(
        target_collection=TeamStatHomeFixtureAssociation.FIXTURE_COLLECTION_NAME,
        attr=TeamStatHomeFixtureAssociation.FIXTURE_ATTRIBUTE_NAME,
        creator=lambda fixture: TeamStatHomeFixtureAssociation(  # type: ignore[arg-type]
            fixture=fixture, kickoff_time=fixture.kickoff_time  # type: ignore[arg-type]
        ),
    )
    home_goals_against = Column(Integer, nullable=False)
    home_goals_for = Column(Integer, nullable=False)
    home_goals_difference = Column(Integer, nullable=False)
    home_matches = Column(Integer, nullable=False)
    home_matches_drawn = Column(Integer, nullable=False)
    home_matches_lost = Column(Integer, nullable=False)
    home_matches_won = Column(Integer, nullable=False)
    home_points = Column(Integer, nullable=False)
    home_position = Column(Integer, nullable=True)
    overall_cumulative_points = Column(ARRAY(Integer), nullable=False)
    overall_fixtures = association_proxy(
        target_collection=TeamStatOverallFixtureAssociation.FIXTURE_COLLECTION_NAME,
        attr=TeamStatOverallFixtureAssociation.FIXTURE_ATTRIBUTE_NAME,
        creator=lambda fixture: TeamStatOverallFixtureAssociation(  # type: ignore[arg-type]
            fixture=fixture, kickoff_time=fixture.kickoff_time  # type: ignore[arg-type]
        ),
    )
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
    season = relationship(SeasonEntity, lazy="selectin", foreign_keys=season_id)
    team_id = Column(String, ForeignKey(TeamEntity.id), nullable=False)
    team = relationship(TeamEntity, lazy="selectin", foreign_keys=team_id)

    def __init__(
        self,
        ground: GroundEntity,
        season: SeasonEntity,
        team: TeamEntity,
    ):
        super().__init__(source_id=self.get_source_id(season, team))
        self.ground_id = ground.id
        self.season_id = season.id
        self.team_id = team.id
        self.initialize()

    @staticmethod
    def get_source_id(season: SeasonEntity, team: TeamEntity) -> str:
        """
        Generates a unique source ID for the team stat based on season and team IDs.
        :param season: Season entity.
        :param team: Team entity.
        :return: Unique source ID.
        """
        return f"{season.source_id}_{team.source_id}"

    # TODO: apply to update
    async def apply_position(self, db_service: DbService, team_stats: list[Self]):
        """
        Applies the position of the team in the standings based on the metrics of other teams.
        :param db_service: Database service to fetch team stats.
        :param team_stats: List of team stats entities to compare against.
        """
        other_overall_metrics, other_home_metrics, other_away_metrics = [], [], []
        for team_stat in team_stats:
            if (
                team_stat.team_id == self.team_id
                or team_stat.season_id != self.season_id
            ):
                continue

            other_overall_metrics.append(
                await team_stat.__compare_overall_standing(db_service, self)
            )
            other_home_metrics.append(team_stat.__compare_home_standing(self))
            other_away_metrics.append(team_stat.__compare_away_standing(self))
        self.overall_position = sum(other >= 0 for other in other_overall_metrics) + 1
        self.home_position = sum(other >= 0 for other in other_home_metrics) + 1
        self.away_position = sum(other >= 0 for other in other_away_metrics) + 1

    def initialize(self):
        """
        Initializes the team statistics entity with default values.
        This method sets the initial values for all attributes related to team statistics.
        """
        self.away_cumulative_points = []
        self.away_goals_against = 0
        self.away_goals_for = 0
        self.away_goals_difference = 0
        self.away_matches = 0
        self.away_matches_drawn = 0
        self.away_matches_lost = 0
        self.away_matches_won = 0
        self.away_points = 0
        self.away_position = None
        self.home_cumulative_points = []
        self.home_goals_against = 0
        self.home_goals_for = 0
        self.home_goals_difference = 0
        self.home_matches = 0
        self.home_matches_drawn = 0
        self.home_matches_lost = 0
        self.home_matches_won = 0
        self.home_points = 0
        self.home_position = None
        self.overall_cumulative_points = []
        self.overall_goals_against = 0
        self.overall_goals_for = 0
        self.overall_goals_difference = 0
        self.overall_matches = 0
        self.overall_matches_drawn = 0
        self.overall_matches_lost = 0
        self.overall_matches_won = 0
        self.overall_points = 0
        self.overall_position = 0

    def __process_fixture(self, fixture: FixtureEntity):
        if fixture.home_team_id == self.team_id:
            is_home = True
            point = fixture.home_point
            goal_against, goal_for = fixture.away_team_score, fixture.home_team_score
            match_won, match_drawn, match_lost = (
                1 if fixture.is_home_won else 0,
                1 if fixture.is_drawn else 0,
                1 if fixture.is_home_lost else 0,
            )
        elif fixture.away_team_id == self.team_id:
            is_home = False
            point = fixture.away_point
            goal_against, goal_for = fixture.home_team_score, fixture.away_team_score
            match_won, match_drawn, match_lost = (
                1 if fixture.is_away_won else 0,
                1 if fixture.is_drawn else 0,
                1 if fixture.is_away_lost else 0,
            )
        else:
            raise ValueError(
                f"Fixture {fixture.id} does not belong to team {self.team_id}."
            )
        goal_difference = goal_for - goal_against
        self.__append_point(self.overall_cumulative_points, point)
        self.overall_fixture_associations.append(
            TeamStatOverallFixtureAssociation(
                team_stat_id=self.id,
                fixture_id=fixture.id,
                kickoff_time=fixture.kickoff_time,
            )
        )
        self.overall_goals_against += goal_against
        self.overall_goals_for += goal_for
        self.overall_goals_difference += goal_difference
        self.overall_matches += 1
        self.overall_matches_drawn += match_drawn
        self.overall_matches_lost += match_lost
        self.overall_matches_won += match_won
        self.overall_points += point
        if is_home:
            self.__append_point(self.home_cumulative_points, point)
            self.home_fixture_associations.append(
                TeamStatHomeFixtureAssociation(
                    team_stat_id=self.id,
                    fixture_id=fixture.id,
                    kickoff_time=fixture.kickoff_time,
                )
            )
            self.home_goals_against += goal_against
            self.home_goals_for += goal_for
            self.home_goals_difference += goal_difference
            self.home_matches += 1
            self.home_matches_drawn += match_drawn
            self.home_matches_lost += match_lost
            self.home_matches_won += match_won
            self.home_points += point
        else:
            self.__append_point(self.away_cumulative_points, point)
            self.away_fixture_associations.append(
                TeamStatAwayFixtureAssociation(
                    team_stat_id=self.id,
                    fixture_id=fixture.id,
                    kickoff_time=fixture.kickoff_time,
                )
            )
            self.away_goals_against += goal_against
            self.away_goals_for += goal_for
            self.away_goals_difference += goal_difference
            self.away_matches += 1
            self.away_matches_drawn += match_drawn
            self.away_matches_lost += match_lost
            self.away_matches_won += match_won
            self.away_points += point

    @staticmethod
    def __append_point(points: list[int], point: int):
        last_point = points[-1] if points else 0
        points.append(last_point + point)

    async def __compare_overall_standing(
        self, db_service: DbService, target: Self
    ) -> int:
        points = compare_ints(self.overall_points, target.overall_points)
        if points != 0:
            return points
        goal_difference = compare_ints(
            self.overall_goals_difference, target.overall_goals_difference
        )
        if goal_difference != 0:
            return goal_difference
        goals_scored = compare_ints(self.overall_goals_for, target.overall_goals_for)
        if goals_scored != 0:
            return goals_scored
        async with db_service.create_db_session() as session:
            merged_entity = await session.merge(self)
            await session.refresh(merged_entity, ["home_fixtures", "away_fixtures"])
            home_match: FixtureEntity | None = next(
                filter(
                    lambda fixture: fixture.away_team_id == target.team_id,
                    merged_entity.home_fixtures,
                ),
                None,
            )
            away_match: FixtureEntity | None = next(
                filter(
                    lambda fixture: fixture.home_team_id == target.team_id,
                    merged_entity.away_fixtures,
                ),
                None,
            )
            self_home_point = home_match.home_point if home_match else 0
            self_away_point = away_match.away_point if away_match else 0
            target_home_point = home_match.away_point if home_match else 0
            target_away_point = away_match.home_point if away_match else 0
        head_to_head_points = compare_ints(
            self_home_point + self_away_point,
            target_home_point + target_away_point,
        )
        if head_to_head_points != 0:
            return head_to_head_points
        return (
            compare_ints(away_match.away_team_score, home_match.away_team_score)
            if home_match is not None and away_match is not None
            else (home_match is None) - (away_match is None)
        )

    def __compare_home_standing(self, target: Self) -> int:
        points = compare_ints(self.home_points, target.home_points)
        if points != 0:
            return points
        goal_difference = compare_ints(
            self.home_goals_difference, target.home_goals_difference
        )
        if goal_difference != 0:
            return goal_difference
        return compare_ints(self.home_goals_for, target.home_goals_for)

    def __compare_away_standing(self, target: Self) -> int:
        points = compare_ints(self.away_points, target.away_points)
        if points != 0:
            return points
        goal_difference = compare_ints(
            self.away_goals_difference, target.away_goals_difference
        )
        if goal_difference != 0:
            return goal_difference
        return compare_ints(self.away_goals_for, target.away_goals_for)
