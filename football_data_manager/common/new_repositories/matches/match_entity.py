from sqlalchemy import Column, String, ForeignKey, Integer, ARRAY

from football_data_manager.common.new_repositories.constants import MATCHES_TABLE_NAME
from football_data_manager.common.new_repositories.fixtures.fixture_entity import (
    FixtureEntity,
)
from football_data_manager.common.new_repositories.officials.official_entity import (
    OfficialEntity,
)
from football_data_manager.common.new_repositories.players.player_entity import (
    PlayerEntity,
)
from football_data_manager.common.new_repositories.pulselive_entity import (
    PulseliveEntity,
)
from football_data_manager.common.new_repositories.staffs.staff_entity import (
    StaffEntity,
)


class MatchEntity(PulseliveEntity):

    __tablename__ = MATCHES_TABLE_NAME

    attendance = Column(Integer, nullable=False)
    away_team_captain_id = Column(String, ForeignKey(PlayerEntity.id), nullable=False)
    away_team_formation = Column(ARRAY(Integer), nullable=False)
    away_team_half_time_score = Column(Integer, nullable=True)
    away_team_manager = Column(String, ForeignKey(StaffEntity.id), nullable=False)
    away_team_score = Column(Integer, nullable=False)
    clock = Column(Integer, nullable=False)
    fixture_id = Column(String, ForeignKey(FixtureEntity.id), nullable=False)
    home_team_captain_id = Column(String, ForeignKey(PlayerEntity.id), nullable=False)
    home_team_formation = Column(ARRAY(Integer), nullable=False)
    home_team_half_time_score = Column(Integer, nullable=True)
    home_team_manager = Column(String, ForeignKey(StaffEntity.id), nullable=False)
    home_team_score = Column(Integer, nullable=False)
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
