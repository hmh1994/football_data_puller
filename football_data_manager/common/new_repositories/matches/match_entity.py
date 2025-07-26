from sqlalchemy import Column, String, ForeignKey, Integer, ARRAY, Double
from sqlalchemy.ext.associationproxy import association_proxy

from football_data_manager.common.new_repositories.constants import MATCHES_TABLE_NAME
from football_data_manager.common.new_repositories.fixtures.fixture_entity import (
    FixtureEntity,
)
from football_data_manager.common.new_repositories.matches.match_away_team_lineup_association import (
    MatchAwayTeamLineupAssociation,
)
from football_data_manager.common.new_repositories.matches.match_away_team_substitute_association import (
    MatchAwayTeamSubstituteAssociation,
)
from football_data_manager.common.new_repositories.matches.match_home_team_lineup_association import (
    MatchHomeTeamLineupAssociation,
)
from football_data_manager.common.new_repositories.matches.match_home_team_substitute_association import (
    MatchHomeTeamSubstituteAssociation,
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

    # https://sdp-prem-prod.premier-league-prod.pulselive.com/api/v3/matches/2444843/stats
    away_team_ball_recovery = Column(Integer, nullable=False)
    away_team_accurate_long_ball = Column(Integer, nullable=False)
    away_team_clearance = Column(Integer, nullable=False)
    away_team_save = Column(Integer, nullable=False)
    away_team_forward_pass = Column(Integer, nullable=False)
    away_team_accurate_cross = Column(Integer, nullable=False)
    away_team_won_duel = Column(Integer, nullable=False)

    away_team_possession = Column(Double, nullable=False)
    away_team_shot = Column(Integer, nullable=False)
    away_team_shot_on_target = Column(Integer, nullable=False)
    away_team_corner = Column(Integer, nullable=False)
    away_team_foul = Column(Integer, nullable=False)
    away_team_yellow_card = Column(Integer, nullable=False)
    away_team_red_card = Column(Integer, nullable=False)
    away_team_offside = Column(Integer, nullable=False)
    away_team_pass = Column(Integer, nullable=False)
    away_team_pass_accuracy = Column(Double, nullable=False)
    away_team_expected_goal = Column(Double, nullable=False)

    away_team_captain_id = Column(String, ForeignKey(PlayerEntity.id), nullable=False)
    away_team_formation = Column(ARRAY(Integer), nullable=False)
    away_team_half_time_score = Column(Integer, nullable=True)
    away_team_manager = Column(String, ForeignKey(StaffEntity.id), nullable=False)
    away_team_lineup = association_proxy(
        target_collection=MatchAwayTeamLineupAssociation.PLAYER_COLLECTION_NAME,
        attr=MatchAwayTeamLineupAssociation.PLAYER_ATTRIBUTE_NAME,
        create=lambda player, row, column: MatchAwayTeamLineupAssociation(  # type: ignore[arg-type]
            player=player,  # type: ignore[arg-type]
            row=row,
            column=column,
        ),
    )
    away_team_score = Column(Integer, nullable=False)
    away_team_substitute = association_proxy(
        target_collection=MatchAwayTeamSubstituteAssociation.PLAYER_COLLECTION_NAME,
        attr=MatchAwayTeamSubstituteAssociation.PLAYER_ATTRIBUTE_NAME,
        create=lambda player: MatchAwayTeamSubstituteAssociation(player=player),  # type: ignore[arg-type]
    )
    clock = Column(Integer, nullable=False)
    fixture_id = Column(String, ForeignKey(FixtureEntity.id), nullable=False)
    full_time_extra_time = Column(Integer, nullable=True)
    half_time_extra_time = Column(Integer, nullable=True)
    home_team_captain_id = Column(String, ForeignKey(PlayerEntity.id), nullable=False)
    home_team_half_time_score = Column(Integer, nullable=True)
    home_team_manager = Column(String, ForeignKey(StaffEntity.id), nullable=False)
    home_team_lineup = association_proxy(
        target_collection=MatchHomeTeamLineupAssociation.POSITION_COLLECTION_NAME,
        attr=MatchHomeTeamLineupAssociation.PLAYER_ATTRIBUTE_NAME,
        create=lambda player, row, column: MatchHomeTeamLineupAssociation(  # type: ignore[arg-type]
            player=player,  # type: ignore[arg-type]
            row=row,
            column=column,
        ),
    )
    home_team_score = Column(Integer, nullable=False)
    home_team_substitute = association_proxy(
        target_collection=MatchHomeTeamSubstituteAssociation.PLAYER_INFO_COLLECTION_NAME,
        attr=MatchHomeTeamSubstituteAssociation.PLAYER_INFO_ATTRIBUTE_NAME,
        create=lambda player: MatchHomeTeamSubstituteAssociation(player=player),  # type: ignore[arg-type]
    )
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
