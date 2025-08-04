from sqlalchemy import Column, String, ForeignKey, Integer, ARRAY, Enum, Boolean
from sqlalchemy.orm import relationship, Mapped

from football_data_manager.common.enums.card_type_enum import CardTypeEnum
from football_data_manager.common.repositories import Base
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


class AbstractMatchCardAssociation(Base):
    """
    Abstract base class for match card associations.

    Provides common functionality for associating cards (yellow/red) with players
    during a match. Used as a base for home and away team card associations.

    :ivar player_id: Foreign key to the player who received the card
    :ivar player: Player entity who received the card
    :ivar card_type: Type of card (yellow or red)
    :ivar clock: Time in minutes when the card was issued
    """

    __abstract__ = True

    player_id = Column(String, ForeignKey(PlayerEntity.id), primary_key=True)
    player = relationship(PlayerEntity, lazy="noload", foreign_keys=player_id)
    card_type = Column(Enum(CardTypeEnum), primary_key=True)
    clock = Column(  # see `order_by` in `match` relationship above
        Integer, nullable=False
    )

    @property
    def card_info(self):
        """
        Get card information as a tuple.

        :returns: Tuple containing player ID, card type, and time
        """
        return self.player.id, self.card_type, self.clock


class AbstractMatchGoalAssociation(Base):
    """
    Abstract base class for match goal associations.

    Provides common functionality for associating goals with players during a match.
    Includes support for assists, penalties, and own goals.

    :ivar player_id: Foreign key to the player who scored the goal
    :ivar player: Player entity who scored the goal
    :ivar assist_player_id: Foreign key to the player who assisted (optional)
    :ivar assist_player: Player entity who provided the assist
    :ivar clock: Time in minutes when the goal was scored
    :ivar is_penalty: Whether the goal was scored from a penalty
    :ivar is_own_goal: Whether the goal was an own goal
    """

    __abstract__ = True

    player_id = Column(String, ForeignKey(PlayerEntity.id), primary_key=True)
    player = relationship(PlayerEntity, lazy="noload", foreign_keys=player_id)
    assist_player_id = Column(String, ForeignKey(PlayerEntity.id), nullable=True)
    assist_player = relationship(
        PlayerEntity,
        lazy="noload",
        foreign_keys=assist_player_id,
    )
    clock = Column(  # see `order_by` in `match` relationship above
        Integer, nullable=False
    )
    is_penalty = Column(Boolean, nullable=False)
    is_own_goal = Column(Boolean, nullable=False)

    @property
    def goal_info(self):
        """
        Get goal information as a tuple.

        :returns: Tuple containing player ID, assist player ID, time, penalty flag, and own goal flag
        """
        return (
            self.player.id,
            self.assist_player.id,
            self.clock,
            self.is_penalty,
            self.is_own_goal,
        )


class AbstractMatchLineupAssociation(Base):
    """
    Abstract base class for match lineup associations.

    Provides common functionality for associating starting lineup players with their
    formation positions and shirt numbers in a match.

    :ivar player_id: Foreign key to the player in the lineup
    :ivar player: Player entity in the starting lineup
    :ivar shirt_number: Player's shirt number for the match
    :ivar row: Formation row position (1-based)
    :ivar column: Formation column position (1-based)
    """

    __abstract__ = True

    player_id = Column(String, ForeignKey(PlayerEntity.id), primary_key=True)
    player = relationship(PlayerEntity, lazy="noload", foreign_keys=player_id)
    shirt_number = Column(  # see `order_by` in `match` relationship above
        Integer, nullable=False
    )
    row = Column(Integer, nullable=False)
    column = Column(Integer, nullable=False)

    @property
    def player_info(self):
        """
        Get player lineup information as a tuple.

        :returns: Tuple containing player ID, shirt number, and position coordinates
        """
        return self.player.id, self.shirt_number, (self.row, self.column)


class AbstractMatchSubstituteAssociation(Base):
    """
    Abstract base class for match substitute associations.

    Provides common functionality for associating substitute players (bench)
    with their shirt numbers in a match.

    :ivar player_id: Foreign key to the substitute player
    :ivar player: Player entity on the substitute bench
    :ivar shirt_number: Player's shirt number for the match
    """

    __abstract__ = True

    player_id = Column(String, ForeignKey(PlayerEntity.id), primary_key=True)
    player = relationship(PlayerEntity, lazy="noload", foreign_keys=player_id)
    shirt_number = Column(  # see `order_by` in `match` relationship above
        Integer, nullable=False
    )

    @property
    def player_info(self):
        """
        Get substitute player information as a tuple.

        :returns: Tuple containing player ID and shirt number
        """
        return self.player.id, self.shirt_number


class AbstractMatchSubstitutionAssociation(Base):
    """
    Abstract base class for match substitution associations.

    Provides common functionality for associating player substitutions (in/out)
    with the time they occurred during a match.

    :ivar in_player_id: Foreign key to the player coming in
    :ivar in_player: Player entity coming into the match
    :ivar out_player_id: Foreign key to the player going out
    :ivar out_player: Player entity being substituted out
    :ivar clock: Time in minutes when the substitution occurred
    """

    __abstract__ = True

    in_player_id = Column(String, ForeignKey(PlayerEntity.id), primary_key=True)
    in_player = relationship(
        PlayerEntity,
        lazy="noload",
        foreign_keys=in_player_id,
    )
    out_player_id = Column(String, ForeignKey(PlayerEntity.id), primary_key=True)
    out_player = relationship(
        PlayerEntity,
        lazy="noload",
        foreign_keys=out_player_id,
    )
    clock = Column(  # see `order_by` in `match` relationship above
        Integer, nullable=False
    )

    @property
    def substitution(self):
        """
        Get substitution information as a tuple.

        :returns: Tuple containing player IDs (in, out) and substitution time
        """
        return (self.in_player.id, self.out_player.id), self.clock


class MatchEntity(PulseliveEntity):
    """
    Entity model for football matches with comprehensive match data.

    Represents a completed football match with detailed information including
    scores, lineups, events, officials, and formations for both teams.
    Extends PulseliveEntity to inherit source tracking functionality.

    :ivar attendance: Number of spectators at the match
    :ivar away_team_captain_id: Foreign key to the away team captain
    :ivar away_team_card_associations: List of cards issued to away team players
    :ivar away_team_formation: Away team formation as array of integers
    :ivar away_team_goal_associations: List of goals scored by away team
    :ivar away_team_half_time_score: Away team score at half-time
    :ivar away_team_lineup_associations: Away team starting lineup
    :ivar away_team_manager: Foreign key to the away team manager
    :ivar away_team_score: Final score of the away team
    :ivar away_team_substitute_associations: Away team substitute players
    :ivar away_team_substitution_associations: Away team substitutions made
    :ivar clock: Total match time in minutes
    :ivar fixture_id: Foreign key to the associated fixture
    :ivar home_team_captain_id: Foreign key to the home team captain
    :ivar home_team_card_associations: List of cards issued to home team players
    :ivar home_team_formation: Home team formation as array of integers
    :ivar home_team_goal_associations: List of goals scored by home team
    :ivar home_team_half_time_score: Home team score at half-time
    :ivar home_team_lineup_associations: Home team starting lineup
    :ivar home_team_manager: Foreign key to the home team manager
    :ivar home_team_score: Final score of the home team
    :ivar home_team_substitute_associations: Home team substitute players
    :ivar home_team_substitution_associations: Home team substitutions made
    :ivar official_main_referee_id: Foreign key to the main referee
    :ivar official_assistant_1_referee_id: Foreign key to first assistant referee
    :ivar official_assistant_2_referee_id: Foreign key to second assistant referee
    :ivar official_fourth_referee_id: Foreign key to the fourth official
    :ivar official_var_id: Foreign key to VAR official (optional)
    :ivar official_assistant_var_id: Foreign key to assistant VAR official (optional)
    """

    __tablename__ = MATCHES_TABLE_NAME

    attendance = Column(Integer, nullable=False)
    away_team_captain_id = Column(String, ForeignKey(PlayerEntity.id), nullable=False)
    away_team_card_associations: Mapped[list[AbstractMatchCardAssociation]]
    away_team_formation = Column(ARRAY(Integer), nullable=False)
    away_team_goal_associations: Mapped[list[AbstractMatchGoalAssociation]]
    away_team_half_time_score = Column(Integer, nullable=True)
    away_team_lineup_associations: Mapped[list[AbstractMatchLineupAssociation]]
    away_team_manager = Column(String, ForeignKey(StaffEntity.id), nullable=False)
    away_team_score = Column(Integer, nullable=False)
    away_team_substitute_associations: Mapped[list[AbstractMatchSubstituteAssociation]]
    away_team_substitution_associations: Mapped[
        list[AbstractMatchSubstitutionAssociation]
    ]
    clock = Column(Integer, nullable=False)
    fixture_id = Column(String, ForeignKey(FixtureEntity.id), nullable=False)
    home_team_captain_id = Column(String, ForeignKey(PlayerEntity.id), nullable=False)
    home_team_card_associations: Mapped[list[AbstractMatchCardAssociation]]
    home_team_formation = Column(ARRAY(Integer), nullable=False)
    home_team_goal_associations: Mapped[list[AbstractMatchGoalAssociation]]
    home_team_half_time_score = Column(Integer, nullable=True)
    home_team_lineup_associations: Mapped[list[AbstractMatchLineupAssociation]]
    home_team_manager = Column(String, ForeignKey(StaffEntity.id), nullable=False)
    home_team_score = Column(Integer, nullable=False)
    home_team_substitute_associations: Mapped[list[AbstractMatchSubstituteAssociation]]
    home_team_substitution_associations: Mapped[
        list[AbstractMatchSubstitutionAssociation]
    ]
    official_main_referee_id = Column(
        String, ForeignKey(OfficialEntity.id), nullable=False
    )
    official_assistant_1_referee_id = Column(
        String, ForeignKey(OfficialEntity.id), nullable=False
    )
    official_assistant_2_referee_id = Column(
        String, ForeignKey(OfficialEntity.id), nullable=False
    )
    official_fourth_referee_id = Column(
        String, ForeignKey(OfficialEntity.id), nullable=False
    )
    official_var_id = Column(String, ForeignKey(OfficialEntity.id), nullable=True)
    official_assistant_var_id = Column(
        String, ForeignKey(OfficialEntity.id), nullable=True
    )

    def __init__(
        self,
        attendance: int,
        away_team_captain: PlayerEntity,
        away_team_manager: StaffEntity,
        away_team_formation: list[int],
        away_team_score: int,
        away_team_half_time_score: int | None,
        clock: int,
        fixture: FixtureEntity,
        home_team_captain: PlayerEntity,
        home_team_manager: StaffEntity,
        home_team_formation: list[int],
        home_team_score: int,
        home_team_half_time_score: int | None,
        official_main_referee: OfficialEntity,
        official_assistant_1_referee: OfficialEntity,
        official_assistant_2_referee: OfficialEntity,
        official_fourth_referee: OfficialEntity,
        official_var: OfficialEntity | None,
        official_assistant_var: OfficialEntity | None,
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
        self.clock = clock

        # Away team information
        self.away_team_captain_id = away_team_captain.id
        self.away_team_manager = away_team_manager.id
        self.away_team_formation = away_team_formation
        self.away_team_score = away_team_score
        self.away_team_half_time_score = away_team_half_time_score

        # Home team information
        self.home_team_captain_id = home_team_captain.id
        self.home_team_manager = home_team_manager.id
        self.home_team_formation = home_team_formation
        self.home_team_score = home_team_score
        self.home_team_half_time_score = home_team_half_time_score

        # Official information
        self.official_main_referee_id = official_main_referee.id
        self.official_assistant_1_referee_id = official_assistant_1_referee.id
        self.official_assistant_2_referee_id = official_assistant_2_referee.id
        self.official_fourth_referee_id = official_fourth_referee.id
        self.official_var_id = official_var.id if official_var else None
        self.official_assistant_var_id = (
            official_assistant_var.id if official_assistant_var else None
        )

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
