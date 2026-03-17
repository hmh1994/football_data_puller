from __future__ import annotations

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from football_data_manager.repository.entities.grounds import GroundEntity
from football_data_manager.repository.entities.match_stats import MatchStatEntity
from football_data_manager.repository.entities.matches import MatchEntity
from football_data_manager.repository.entities.player_stats import PlayerStatEntity
from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.entities.staffs import StaffEntity
from football_data_manager.repository.entities.team_stat_match_association import (
    TeamStatMatchAssociation,
)
from football_data_manager.repository.entities.team_stats import TeamStatEntity
from football_data_manager.repository.entities.teams import TeamEntity
from football_data_manager.validator.validators.base import (
    AbstractValidator,
    ValidationResult,
)


class TeamStatValidator(AbstractValidator):
    """TeamStat entity validation."""

    async def validate(
        self,
        season_id: str | None = None,
        competition_id: str | None = None,
    ) -> ValidationResult:
        result = ValidationResult(entity="team-stat")

        async with self._session_factory.session() as session:
            season_ids = await self._resolve_scoped_season_ids(
                session=session,
                season_id=season_id,
                competition_id=competition_id,
            )

            stmt = select(TeamStatEntity).options(
                selectinload(TeamStatEntity.match_associations)
            )
            if season_id or competition_id:
                if not season_ids:
                    result.add_warning(
                        "data_exists",
                        detail="No TeamStat records matched the given scope",
                    )
                    return result
                stmt = stmt.where(TeamStatEntity.season_id.in_(season_ids))

            team_stats = (await session.execute(stmt)).scalars().all()
            if not team_stats:
                result.add_warning("data_exists", detail="No TeamStat records found")
                return result

            team_ids = await self._load_id_set(session, TeamEntity)
            season_fk_ids = await self._load_id_set(session, SeasonEntity)
            ground_ids = await self._load_id_set(session, GroundEntity)
            staff_ids = await self._load_id_set(session, StaffEntity)

            match_map = {
                match_value.id: match_value
                for match_value in (
                    await session.execute(select(MatchEntity))
                ).scalars()
            }
            match_stat_map = {
                (match_stat.match_id, match_stat.team_id): match_stat
                for match_stat in (
                    await session.execute(select(MatchStatEntity))
                ).scalars()
            }
            player_goal_totals: dict[tuple[str, str], int] = defaultdict(int)
            for team_id_value, season_id_value, goals in (
                await session.execute(
                    select(
                        PlayerStatEntity.team_id,
                        PlayerStatEntity.season_id,
                        PlayerStatEntity.shooting_goals,
                    )
                )
            ).all():
                player_goal_totals[(team_id_value, season_id_value)] += goals or 0

            for team_stat in team_stats:
                entity_id = team_stat.id
                self._check_self_consistency(result, team_stat)
                self._check_stat_fields(result, team_stat)
                self.check_fk_exists(
                    result,
                    "team_id FK",
                    team_stat.team_id,
                    team_ids,
                    entity_id,
                )
                self.check_fk_exists(
                    result,
                    "season_id FK",
                    team_stat.season_id,
                    season_fk_ids,
                    entity_id,
                )
                self.check_fk_exists(
                    result,
                    "ground_id FK",
                    team_stat.ground_id,
                    ground_ids,
                    entity_id,
                )
                self.check_fk_exists(
                    result,
                    "manager_id FK",
                    team_stat.manager_id,
                    staff_ids,
                    entity_id,
                )

                associations = list(team_stat.match_associations)
                self.check_equal(
                    result,
                    "overall_matches == len(match_associations)",
                    team_stat.overall_matches,
                    len(associations),
                    entity_id,
                )

                goals_for = 0
                goals_against = 0
                yellow_cards = 0
                red_cards = 0
                corners = 0
                shots_total = 0
                shots_on_target = 0
                clean_sheets = 0
                blocks = 0
                interceptions = 0
                tackles = 0
                tackles_won = 0

                for association in associations:
                    match_value = match_map.get(association.match_id)
                    if match_value is None:
                        continue

                    if association.is_home:
                        goals_for += match_value.home_team_score
                        goals_against += match_value.away_team_score
                        if match_value.away_team_score == 0:
                            clean_sheets += 1
                    else:
                        goals_for += match_value.away_team_score
                        goals_against += match_value.home_team_score
                        if match_value.home_team_score == 0:
                            clean_sheets += 1

                    match_stat = match_stat_map.get((association.match_id, team_stat.team_id))
                    if match_stat is None:
                        continue
                    yellow_cards += match_stat.discipline_yellow_cards
                    red_cards += match_stat.discipline_red_cards
                    corners += match_stat.corners
                    shots_total += match_stat.shots_total
                    shots_on_target += match_stat.shots_on_target
                    blocks += match_stat.defense_blocks
                    interceptions += match_stat.defense_interceptions
                    tackles += match_stat.defense_tackles_total
                    tackles_won += match_stat.defense_tackles_won

                self.check_equal(
                    result,
                    "overall_goals_for == sum(match goals for)",
                    team_stat.overall_goals_for,
                    goals_for,
                    entity_id,
                )
                self.check_equal(
                    result,
                    "overall_goals_against == sum(match goals against)",
                    team_stat.overall_goals_against,
                    goals_against,
                    entity_id,
                )
                self.check_equal(
                    result,
                    "overall_stat_discipline_yellow_cards == sum(match_stat yellow_cards)",
                    team_stat.overall_stat_discipline_yellow_cards or 0,
                    yellow_cards,
                    entity_id,
                )
                self.check_equal(
                    result,
                    "overall_stat_discipline_red_cards == sum(match_stat red_cards)",
                    team_stat.overall_stat_discipline_red_cards or 0,
                    red_cards,
                    entity_id,
                )
                self.check_equal(
                    result,
                    "overall_stat_attack_corners == sum(match_stat corners)",
                    team_stat.overall_stat_attack_corners or 0,
                    corners,
                    entity_id,
                )
                self.check_equal(
                    result,
                    "overall_stat_attack_total_shots == sum(match_stat shots_total)",
                    team_stat.overall_stat_attack_total_shots or 0,
                    shots_total,
                    entity_id,
                )
                self.check_equal(
                    result,
                    "overall_stat_attack_shots_on_target == sum(match_stat shots_on_target)",
                    team_stat.overall_stat_attack_shots_on_target or 0,
                    shots_on_target,
                    entity_id,
                )
                self.check_equal(
                    result,
                    "overall_stat_defense_clean_sheets == clean_sheet_count",
                    team_stat.overall_stat_defense_clean_sheets or 0,
                    clean_sheets,
                    entity_id,
                )
                self.check_equal(
                    result,
                    "overall_stat_defense_blocks == sum(match_stat defense_blocks)",
                    team_stat.overall_stat_defense_blocks or 0,
                    blocks,
                    entity_id,
                )
                self.check_equal(
                    result,
                    "overall_stat_defense_interceptions == sum(match_stat interceptions)",
                    team_stat.overall_stat_defense_interceptions or 0,
                    interceptions,
                    entity_id,
                )
                self.check_equal(
                    result,
                    "overall_stat_defense_tackles == sum(match_stat defense_tackles_total)",
                    team_stat.overall_stat_defense_tackles or 0,
                    tackles,
                    entity_id,
                )
                self.check_equal(
                    result,
                    "overall_stat_defense_tackles_successful == sum(match_stat defense_tackles_won)",
                    team_stat.overall_stat_defense_tackles_successful or 0,
                    tackles_won,
                    entity_id,
                )
                self.check_equal(
                    result,
                    "overall_goals_for ~= sum(PlayerStat.shooting_goals)",
                    team_stat.overall_goals_for,
                    player_goal_totals.get((team_stat.team_id, team_stat.season_id), 0),
                    entity_id,
                    tolerance=2.0,
                )

        return result

    def _check_self_consistency(
        self,
        result: ValidationResult,
        team_stat: TeamStatEntity,
    ) -> None:
        entity_id = team_stat.id
        self.check_equal(
            result,
            "overall_matches == won + drawn + lost",
            team_stat.overall_matches,
            team_stat.overall_matches_won
            + team_stat.overall_matches_drawn
            + team_stat.overall_matches_lost,
            entity_id,
        )
        self.check_equal(
            result,
            "home_matches == won + drawn + lost",
            team_stat.home_matches,
            team_stat.home_matches_won
            + team_stat.home_matches_drawn
            + team_stat.home_matches_lost,
            entity_id,
        )
        self.check_equal(
            result,
            "away_matches == won + drawn + lost",
            team_stat.away_matches,
            team_stat.away_matches_won
            + team_stat.away_matches_drawn
            + team_stat.away_matches_lost,
            entity_id,
        )
        self.check_equal(
            result,
            "overall_matches == home + away",
            team_stat.overall_matches,
            team_stat.home_matches + team_stat.away_matches,
            entity_id,
        )
        self.check_equal(
            result,
            "overall_matches_won == home + away won",
            team_stat.overall_matches_won,
            team_stat.home_matches_won + team_stat.away_matches_won,
            entity_id,
        )
        self.check_equal(
            result,
            "overall_matches_drawn == home + away drawn",
            team_stat.overall_matches_drawn,
            team_stat.home_matches_drawn + team_stat.away_matches_drawn,
            entity_id,
        )
        self.check_equal(
            result,
            "overall_matches_lost == home + away lost",
            team_stat.overall_matches_lost,
            team_stat.home_matches_lost + team_stat.away_matches_lost,
            entity_id,
        )
        self.check_equal(
            result,
            "overall_goals_for == home + away",
            team_stat.overall_goals_for,
            team_stat.home_goals_for + team_stat.away_goals_for,
            entity_id,
        )
        self.check_equal(
            result,
            "overall_goals_against == home + away",
            team_stat.overall_goals_against,
            team_stat.home_goals_against + team_stat.away_goals_against,
            entity_id,
        )
        self.check_equal(
            result,
            "overall_goals_difference == for - against",
            team_stat.overall_goals_difference,
            team_stat.overall_goals_for - team_stat.overall_goals_against,
            entity_id,
        )
        self.check_equal(
            result,
            "home_goals_difference == for - against",
            team_stat.home_goals_difference,
            team_stat.home_goals_for - team_stat.home_goals_against,
            entity_id,
        )
        self.check_equal(
            result,
            "away_goals_difference == for - against",
            team_stat.away_goals_difference,
            team_stat.away_goals_for - team_stat.away_goals_against,
            entity_id,
        )
        self.check_equal(
            result,
            "overall_goals_difference == home + away difference",
            team_stat.overall_goals_difference,
            team_stat.home_goals_difference + team_stat.away_goals_difference,
            entity_id,
        )
        self.check_equal(
            result,
            "overall_points == 3*won + drawn",
            team_stat.overall_points,
            3 * team_stat.overall_matches_won + team_stat.overall_matches_drawn,
            entity_id,
        )
        self.check_equal(
            result,
            "home_points == 3*won + drawn",
            team_stat.home_points,
            3 * team_stat.home_matches_won + team_stat.home_matches_drawn,
            entity_id,
        )
        self.check_equal(
            result,
            "away_points == 3*won + drawn",
            team_stat.away_points,
            3 * team_stat.away_matches_won + team_stat.away_matches_drawn,
            entity_id,
        )
        self.check_equal(
            result,
            "overall_points == home + away points",
            team_stat.overall_points,
            team_stat.home_points + team_stat.away_points,
            entity_id,
        )

        for label, cumulative_points, matches_count, total_points in [
            (
                "overall",
                team_stat.overall_cumulative_points,
                team_stat.overall_matches,
                team_stat.overall_points,
            ),
            (
                "home",
                team_stat.home_cumulative_points,
                team_stat.home_matches,
                team_stat.home_points,
            ),
            (
                "away",
                team_stat.away_cumulative_points,
                team_stat.away_matches,
                team_stat.away_points,
            ),
        ]:
            self.check_equal(
                result,
                f"len({label}_cumulative_points) == {label}_matches",
                len(cumulative_points),
                matches_count,
                entity_id,
            )
            if cumulative_points:
                self.check_equal(
                    result,
                    f"{label}_cumulative_points[-1] == {label}_points",
                    cumulative_points[-1],
                    total_points,
                    entity_id,
                )
                deltas = [
                    later - earlier
                    for earlier, later in zip(cumulative_points, cumulative_points[1:])
                ]
                valid_deltas = all(delta in {0, 1, 3} for delta in deltas)
                self.check_true(
                    result,
                    f"{label}_cumulative_points delta in {{0,1,3}}",
                    valid_deltas,
                    entity_id,
                    detail=f"deltas={deltas}",
                )

        for rule, value in {
            "overall_position >= 1": team_stat.overall_position,
            "home_position >= 1": team_stat.home_position,
            "away_position >= 1": team_stat.away_position,
        }.items():
            if value is not None:
                self.check_true(
                    result,
                    rule,
                    value >= 1,
                    entity_id,
                    detail=f"value={value}",
                )

    def _check_stat_fields(
        self,
        result: ValidationResult,
        team_stat: TeamStatEntity,
    ) -> None:
        entity_id = team_stat.id
        self.check_lte(
            result,
            "overall_stat_attack_passes_successful <= overall_stat_attack_passes",
            team_stat.overall_stat_attack_passes_successful,
            team_stat.overall_stat_attack_passes,
            entity_id,
        )
        self.check_lte(
            result,
            "overall_stat_attack_crosses_successful <= overall_stat_attack_crosses",
            team_stat.overall_stat_attack_crosses_successful,
            team_stat.overall_stat_attack_crosses,
            entity_id,
        )
        self.check_lte(
            result,
            "overall_stat_attack_long_balls_successful <= overall_stat_attack_long_balls",
            team_stat.overall_stat_attack_long_balls_successful,
            team_stat.overall_stat_attack_long_balls,
            entity_id,
        )
        self.check_lte(
            result,
            "overall_stat_defense_tackles_successful <= overall_stat_defense_tackles",
            team_stat.overall_stat_defense_tackles_successful,
            team_stat.overall_stat_defense_tackles,
            entity_id,
        )
        self.check_lte(
            result,
            "overall_stat_defense_duels_won <= overall_stat_defense_duels_total",
            team_stat.overall_stat_defense_duels_won,
            team_stat.overall_stat_defense_duels_total,
            entity_id,
        )
        self.check_lte(
            result,
            "overall_stat_defense_duels_aerial_won <= overall_stat_defense_duels_aerial_total",
            team_stat.overall_stat_defense_duels_aerial_won,
            team_stat.overall_stat_defense_duels_aerial_total,
            entity_id,
        )
        self.check_lte(
            result,
            "overall_stat_defense_duels_ground_won <= overall_stat_defense_duels_ground_total",
            team_stat.overall_stat_defense_duels_ground_won,
            team_stat.overall_stat_defense_duels_ground_total,
            entity_id,
        )
        self.check_equal(
            result,
            "overall_stat_defense_duels_total == aerial_total + ground_total",
            team_stat.overall_stat_defense_duels_total or 0,
            (team_stat.overall_stat_defense_duels_aerial_total or 0)
            + (team_stat.overall_stat_defense_duels_ground_total or 0),
            entity_id,
        )
        self.check_equal(
            result,
            "overall_stat_defense_duels_won == aerial_won + ground_won",
            team_stat.overall_stat_defense_duels_won or 0,
            (team_stat.overall_stat_defense_duels_aerial_won or 0)
            + (team_stat.overall_stat_defense_duels_ground_won or 0),
            entity_id,
        )
        self.check_lte(
            result,
            "overall_stat_discipline_red_cards_direct <= overall_stat_discipline_red_cards",
            team_stat.overall_stat_discipline_red_cards_direct,
            team_stat.overall_stat_discipline_red_cards,
            entity_id,
        )
        self.check_range(
            result,
            "overall_stat_average_possession in [0, 100]",
            team_stat.overall_stat_average_possession,
            0.0,
            100.0,
            entity_id,
        )
        self.check_lte(
            result,
            "overall_stat_attack_shots_on_target <= overall_stat_attack_total_shots",
            team_stat.overall_stat_attack_shots_on_target,
            team_stat.overall_stat_attack_total_shots,
            entity_id,
        )
        for field_name in self.integer_field_names(TeamStatEntity):
            if field_name.endswith("_goals_difference"):
                continue
            self.check_non_negative(
                result,
                f"{field_name} >= 0",
                getattr(team_stat, field_name),
                entity_id,
            )
        self.check_non_negative(
            result,
            "overall_stat_attack_expected_goals >= 0.0",
            team_stat.overall_stat_attack_expected_goals,
            entity_id,
        )
        self.check_non_negative(
            result,
            "overall_stat_attack_expected_assists >= 0.0",
            team_stat.overall_stat_attack_expected_assists,
            entity_id,
        )
