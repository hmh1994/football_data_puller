from sqlalchemy import Column, String, ForeignKey, Integer, ARRAY, Enum

from football_data_manager.common.enums.period_enum import PeriodEnum
from football_data_manager.common.repositories.constants import MATCHES_TABLE_NAME
from football_data_manager.common.repositories.fixtures.fixture_entity import (
    FixtureEntity,
)
from football_data_manager.common.repositories.officials.official_entity import (
    OfficialEntity,
)
from football_data_manager.common.repositories.players.player_entity import (
    PlayerEntity,
)
from football_data_manager.common.repositories.pulselive_entity import (
    PulseliveEntity,
)
from football_data_manager.common.repositories.staffs.staff_entity import (
    StaffEntity,
)
from football_data_manager.common.repositories.teams.team_entity import TeamEntity


class MatchEntity(PulseliveEntity):
    """
    Entity model for football matches with comprehensive match data.

    Represents a completed football match with detailed information including
    scores, lineups, events, officials, and formations for both teams.
    Extends PulseliveEntity to inherit source tracking functionality.

    :ivar attendance: Number of spectators at the match
    :ivar away_team_captain_id: Foreign key to the away team captain
    :ivar away_team_formation: Away team formation as array of integers
    :ivar away_team_half_time_score: Away team score at half-time
    :ivar away_team_manager: Foreign key to the away team manager
    :ivar away_team_score: Final score of the away team
    :ivar card_associations: List of cards issued to both team players with is_home flag
    :ivar clock: Total match time in minutes
    :ivar fixture_id: Foreign key to the associated fixture
    :ivar goal_associations: List of goals scored by both team players with is_home flag
    :ivar home_team_captain_id: Foreign key to the home team captain
    :ivar home_team_formation: Home team formation as array of integers
    :ivar home_team_half_time_score: Home team score at half-time
    :ivar lineup_associations: List of players in starting lineup with is_home flag
    :ivar home_team_manager: Foreign key to the home team manager
    :ivar home_team_score: Final score of the home team
    :ivar substitute_associations: List of substitute players with is_home flag
    :ivar substitution_associations: List of substitutions made with is_home flag
    :ivar official_main_referee_id: Foreign key to the main referee
    :ivar official_assistant_1_referee_id: Foreign key to first assistant referee
    :ivar official_assistant_2_referee_id: Foreign key to second assistant referee
    :ivar official_fourth_referee_id: Foreign key to the fourth official
    :ivar official_var_id: Foreign key to VAR official (optional)
    :ivar official_assistant_var_id: Foreign key to assistant VAR official (optional)
    """

    __tablename__ = MATCHES_TABLE_NAME

    attendance = Column(Integer, nullable=True)
    away_team_captain_id = Column(
        String,
        ForeignKey(PlayerEntity.id, ondelete="SET NULL", onupdate="RESTRICT"),
        nullable=True,
    )
    away_team_formation = Column(ARRAY(Integer), nullable=False)
    away_team_half_time_score = Column(Integer, nullable=True)
    away_team_id = Column(
        String,
        ForeignKey(TeamEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
    )
    away_team_manager = Column(
        String,
        ForeignKey(StaffEntity.id, ondelete="SET NULL", onupdate="RESTRICT"),
        nullable=True,
    )
    away_team_score = Column(Integer, nullable=False)
    clock = Column(Integer, nullable=False)
    fixture_id = Column(
        String,
        ForeignKey(FixtureEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
    )
    home_team_captain_id = Column(
        String,
        ForeignKey(PlayerEntity.id, ondelete="SET NULL", onupdate="RESTRICT"),
        nullable=True,
    )
    home_team_formation = Column(ARRAY(Integer), nullable=False)
    home_team_half_time_score = Column(Integer, nullable=True)
    home_team_id = Column(
        String,
        ForeignKey(TeamEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
    )
    home_team_manager = Column(
        String,
        ForeignKey(StaffEntity.id, ondelete="SET NULL", onupdate="RESTRICT"),
        nullable=True,
    )
    home_team_score = Column(Integer, nullable=False)
    official_main_referee_id = Column(
        String,
        ForeignKey(OfficialEntity.id, ondelete="SET NULL", onupdate="RESTRICT"),
        nullable=True,
    )
    official_assistant_1_referee_id = Column(
        String,
        ForeignKey(OfficialEntity.id, ondelete="SET NULL", onupdate="RESTRICT"),
        nullable=True,
    )
    official_assistant_2_referee_id = Column(
        String,
        ForeignKey(OfficialEntity.id, ondelete="SET NULL", onupdate="RESTRICT"),
        nullable=True,
    )
    official_fourth_referee_id = Column(
        String,
        ForeignKey(OfficialEntity.id, ondelete="SET NULL", onupdate="RESTRICT"),
        nullable=True,
    )
    official_var_id = Column(
        String,
        ForeignKey(OfficialEntity.id, ondelete="SET NULL", onupdate="RESTRICT"),
        nullable=True,
    )
    official_assistant_var_id = Column(
        String,
        ForeignKey(OfficialEntity.id, ondelete="SET NULL", onupdate="RESTRICT"),
        nullable=True,
    )
    period = Column(Enum(PeriodEnum), nullable=False)

    def __init__(
        self,
        attendance: int,
        away_team_captain: PlayerEntity | None,
        away_team_manager: StaffEntity | None,
        away_team_formation: list[int],
        away_team_score: int,
        away_team_half_time_score: int | None,
        clock: int | None,
        fixture: FixtureEntity,
        home_team_captain: PlayerEntity | None,
        home_team_manager: StaffEntity | None,
        home_team_formation: list[int],
        home_team_score: int,
        home_team_half_time_score: int | None,
        official_main_referee: OfficialEntity | None,
        official_assistant_1_referee: OfficialEntity | None,
        official_assistant_2_referee: OfficialEntity | None,
        official_fourth_referee: OfficialEntity | None,
        official_var: OfficialEntity | None,
        official_assistant_var: OfficialEntity | None,
        period: PeriodEnum,
    ):
        """
        Initialize a new MatchEntity instance.

        :param attendance: Number of spectators at the match
        :param away_team_captain: Player entity representing the away team captain
        :param away_team_manager: Staff entity representing the away team manager
        :param away_team_formation: Formation array for the away team (e.g., [4, 4, 2])
        :param away_team_score: Final score of the away team
        :param away_team_half_time_score: Away team score at half-time (optional)
        :param clock: Total match time in minutes
        :param fixture: Fixture entity this match is associated with
        :param home_team_captain: Player entity representing the home team captain
        :param home_team_manager: Staff entity representing the home team manager
        :param home_team_formation: Formation array for the home team (e.g., [4, 4, 2])
        :param home_team_score: Final score of the home team
        :param home_team_half_time_score: Home team score at half-time (optional)
        :param official_main_referee: Main referee officiating the match
        :param official_assistant_1_referee: First assistant referee
        :param official_assistant_2_referee: Second assistant referee
        :param official_fourth_referee: Fourth official
        :param official_var: VAR official (optional)
        :param official_assistant_var: Assistant VAR official (optional)
        """
        super().__init__(source_id=fixture.source_id)
        # Connect to fixture
        self.fixture_id = fixture.id

        # Basic fields
        self.attendance = attendance
        self.clock = clock if clock else 0
        self.period = period

        # Away team information
        self.away_team_id = fixture.away_team_id
        self.away_team_captain_id = away_team_captain.id if away_team_captain else None
        self.away_team_manager = away_team_manager.id if away_team_manager else None
        self.away_team_formation = away_team_formation
        self.away_team_score = away_team_score if away_team_score else 0
        self.away_team_half_time_score = away_team_half_time_score

        # Home team information
        self.home_team_id = fixture.home_team_id
        self.home_team_captain_id = home_team_captain.id if home_team_captain else None
        self.home_team_manager = home_team_manager.id if home_team_manager else None
        self.home_team_formation = home_team_formation
        self.home_team_score = home_team_score if home_team_score else 0
        self.home_team_half_time_score = home_team_half_time_score

        # Official information
        self.official_main_referee_id = (
            official_main_referee.id if official_main_referee else None
        )
        self.official_assistant_1_referee_id = (
            official_assistant_1_referee.id if official_assistant_1_referee else None
        )
        self.official_assistant_2_referee_id = (
            official_assistant_2_referee.id if official_assistant_2_referee else None
        )
        self.official_fourth_referee_id = (
            official_fourth_referee.id if official_fourth_referee else None
        )
        self.official_var_id = official_var.id if official_var else None
        self.official_assistant_var_id = (
            official_assistant_var.id if official_assistant_var else None
        )

        # Associations
        self.card_associations = []
        self.goal_associations = []
        self.lineup_associations = []
        self.substitute_associations = []
        self.substitution_associations = []

    @property
    def is_home_won(self) -> bool | None:
        """
        Check if the home team won the match.

        :returns: True if home team won, False if away team won, None if scores unavailable
        """
        if self.home_team_score is None or self.away_team_score is None:
            return None
        else:
            return self.home_team_score > self.away_team_score

    @property
    def is_away_won(self) -> bool | None:
        """
        Check if the away team won the match.

        :returns: True if away team won, False if home team won, None if scores unavailable
        """
        if self.away_team_score is None or self.home_team_score is None:
            return None
        else:
            return self.away_team_score > self.home_team_score

    @property
    def is_drawn(self) -> bool | None:
        """
        Check if the match ended in a draw.

        :returns: True if match was drawn, False otherwise, None if scores unavailable
        """
        if self.home_team_score is None or self.away_team_score is None:
            return None
        else:
            return self.home_team_score == self.away_team_score

    @property
    def is_home_lost(self) -> bool | None:
        """
        Check if the home team lost the match.

        :returns: True if home team lost, False otherwise, None if scores unavailable
        """
        if self.is_home_won is None:
            return None
        else:
            return not self.is_home_won and not self.is_drawn

    @property
    def is_away_lost(self) -> bool | None:
        """
        Check if the away team lost the match.

        :returns: True if away team lost, False otherwise, None if scores unavailable
        """
        if self.is_away_won is None:
            return None
        else:
            return not self.is_away_won and not self.is_drawn

    @property
    def away_point(self) -> int | None:
        """
        Get the away team points based on match result.

        Uses standard football scoring: 3 points for win, 1 for draw, 0 for loss.

        :returns: Points earned by away team (3/1/0), or None if scores unavailable
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
        Get the home team points based on match result.

        Uses standard football scoring: 3 points for win, 1 for draw, 0 for loss.

        :returns: Points earned by home team (3/1/0), or None if scores unavailable
        """
        if self.is_home_won:
            return 3
        elif self.is_drawn:
            return 1
        elif self.is_home_lost:
            return 0
        else:
            return None
