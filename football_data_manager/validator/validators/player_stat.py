from __future__ import annotations

from collections import defaultdict

from sqlalchemy import select

from football_data_manager.repository.entities.fixtures import FixtureEntity
from football_data_manager.repository.entities.matches import MatchEntity
from football_data_manager.repository.entities.player_championship_association import (
    PlayerChampionshipAssociation,
)
from football_data_manager.repository.entities.player_stats import PlayerStatEntity
from football_data_manager.repository.entities.players import PlayerEntity
from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.entities.team_championship_association import (
    TeamChampionshipAssociation,
)
from football_data_manager.repository.entities.teams import TeamEntity
from football_data_manager.validator.validators.base import (
    AbstractValidator,
    ValidationResult,
)


class PlayerStatValidator(AbstractValidator):
    """PlayerStat entity validation."""

    async def validate(
        self,
        season_id: str | None = None,
        competition_id: str | None = None,
    ) -> ValidationResult:
        result = ValidationResult(entity="player-stat")

        async with self._session_factory.session() as session:
            season_ids = await self._resolve_scoped_season_ids(
                session=session,
                season_id=season_id,
                competition_id=competition_id,
            )

            stmt = select(PlayerStatEntity)
            if season_id or competition_id:
                if not season_ids:
                    result.add_warning(
                        "data_exists",
                        detail="No PlayerStat records matched the given scope",
                    )
                    return result
                stmt = stmt.where(PlayerStatEntity.season_id.in_(season_ids))

            player_stats = (await session.execute(stmt)).scalars().all()
            if not player_stats:
                result.add_warning("data_exists", detail="No PlayerStat records found")
                return result

            player_ids = await self._load_id_set(session, PlayerEntity)
            team_ids = await self._load_id_set(session, TeamEntity)
            season_fk_ids = await self._load_id_set(session, SeasonEntity)

            season_team_match_counts: dict[tuple[str, str], int] = defaultdict(int)
            for season_id_value, home_team_id, away_team_id in (
                await session.execute(
                    select(
                        FixtureEntity.season_id,
                        MatchEntity.home_team_id,
                        MatchEntity.away_team_id,
                    ).join(MatchEntity, MatchEntity.fixture_id == FixtureEntity.id)
                )
            ).all():
                season_team_match_counts[(season_id_value, home_team_id)] += 1
                season_team_match_counts[(season_id_value, away_team_id)] += 1

            player_season_memberships: dict[str, set[str]] = defaultdict(set)
            for player_id_value, player_season_id in (
                await session.execute(
                    select(
                        PlayerChampionshipAssociation.player_id,
                        PlayerChampionshipAssociation.season_id,
                    )
                )
            ).all():
                player_season_memberships[player_id_value].add(player_season_id)

            seasons_with_pca: set[str] = {
                player_season_id
                for memberships in player_season_memberships.values()
                for player_season_id in memberships
            }

            team_season_memberships: set[tuple[str, str]] = {
                (team_id_value, team_season_id)
                for team_id_value, team_season_id in (
                    await session.execute(
                        select(
                            TeamChampionshipAssociation.team_id,
                            TeamChampionshipAssociation.season_id,
                        )
                    )
                ).all()
            }
            seasons_with_tca: set[str] = {
                season_id_value for _, season_id_value in team_season_memberships
            }

            for player_stat in player_stats:
                entity_id = player_stat.id
                self.check_non_negative(
                    result,
                    "appearances >= 0",
                    player_stat.appearances,
                    entity_id,
                )
                self.check_non_negative(
                    result,
                    "minutes_played >= 0",
                    player_stat.minutes_played,
                    entity_id,
                )
                if player_stat.number in (None, 0):
                    result.add_skip("number >= 1", entity_id)
                else:
                    self.check_true(
                        result,
                        "number >= 1",
                        player_stat.number >= 1,
                        entity_id,
                        detail=f"number={player_stat.number}",
                    )
                for score_field in [
                    "score_shooting",
                    "score_passing",
                    "score_defending",
                    "score_dribbling",
                    "score_discipline",
                    "score_overall",
                ]:
                    self.check_range(
                        result,
                        f"{score_field} in [0, 100]",
                        getattr(player_stat, score_field),
                        0.0,
                        100.0,
                        entity_id,
                    )

                self.check_lte(
                    result,
                    "shooting_goals_penalty <= shooting_penalties_taken",
                    player_stat.shooting_goals_penalty,
                    player_stat.shooting_penalties_taken,
                    entity_id,
                )
                self.check_lte(
                    result,
                    "shooting_shots_on_target <= shooting_shots",
                    player_stat.shooting_shots_on_target,
                    player_stat.shooting_shots,
                    entity_id,
                )
                self.check_non_negative(
                    result,
                    "shooting_expected_goals >= 0.0",
                    player_stat.shooting_expected_goals,
                    entity_id,
                )
                self.check_lte(
                    result,
                    "shooting_expected_goals_non_penalty <= shooting_expected_goals",
                    player_stat.shooting_expected_goals_non_penalty,
                    player_stat.shooting_expected_goals,
                    entity_id,
                )
                if (
                    player_stat.shooting_expected_goals is not None
                    and player_stat.shooting_expected_goals_non_penalty is not None
                    and player_stat.shooting_penalties_taken is not None
                ):
                    expected = (
                        player_stat.shooting_expected_goals
                        - 0.79 * player_stat.shooting_penalties_taken
                    )
                    self.check_equal(
                        result,
                        "shooting_expected_goals_non_penalty derived",
                        player_stat.shooting_expected_goals_non_penalty,
                        expected,
                        entity_id,
                        tolerance=0.2,
                    )
                self.check_non_negative(
                    result,
                    "shooting_goals >= 0",
                    player_stat.shooting_goals,
                    entity_id,
                )

                self.check_lte(
                    result,
                    "passing_passes_successful <= passing_passes_total",
                    player_stat.passing_passes_successful,
                    player_stat.passing_passes_total,
                    entity_id,
                )
                self.check_lte(
                    result,
                    "passing_crosses_successful <= passing_crosses_total",
                    player_stat.passing_crosses_successful,
                    player_stat.passing_crosses_total,
                    entity_id,
                )
                self.check_lte(
                    result,
                    "passing_long_balls_accurate <= passing_long_balls_total",
                    player_stat.passing_long_balls_accurate,
                    player_stat.passing_long_balls_total,
                    entity_id,
                )
                self.check_non_negative(
                    result,
                    "passing_assists >= 0",
                    player_stat.passing_assists,
                    entity_id,
                )
                if (
                    player_stat.passing_chances_created is not None
                    and player_stat.passing_assists is not None
                ):
                    self.check_true(
                        result,
                        "passing_chances_created >= passing_assists",
                        player_stat.passing_chances_created
                        >= player_stat.passing_assists,
                        entity_id,
                        detail=(
                            f"chances_created={player_stat.passing_chances_created}, "
                            f"assists={player_stat.passing_assists}"
                        ),
                    )
                self.check_non_negative(
                    result,
                    "passing_expected_assists >= 0.0",
                    player_stat.passing_expected_assists,
                    entity_id,
                )

                self.check_lte(
                    result,
                    "defending_tackles_won <= defending_tackles_total",
                    player_stat.defending_tackles_won,
                    player_stat.defending_tackles_total,
                    entity_id,
                )
                self.check_lte(
                    result,
                    "defending_duels_won <= defending_duels_total",
                    player_stat.defending_duels_won,
                    player_stat.defending_duels_total,
                    entity_id,
                )
                self.check_lte(
                    result,
                    "defending_duels_aerial_won <= defending_duels_aerial_total",
                    player_stat.defending_duels_aerial_won,
                    player_stat.defending_duels_aerial_total,
                    entity_id,
                )
                self.check_lte(
                    result,
                    "defending_duels_ground_won <= defending_duels_ground_total",
                    player_stat.defending_duels_ground_won,
                    player_stat.defending_duels_ground_total,
                    entity_id,
                )
                if (
                    player_stat.defending_duels_total is not None
                    and player_stat.defending_duels_aerial_total is not None
                    and player_stat.defending_duels_ground_total is not None
                ):
                    self.check_equal(
                        result,
                        "defending_duels_total == aerial_total + ground_total",
                        player_stat.defending_duels_total,
                        player_stat.defending_duels_aerial_total
                        + player_stat.defending_duels_ground_total,
                        entity_id,
                    )
                if (
                    player_stat.defending_duels_won is not None
                    and player_stat.defending_duels_aerial_won is not None
                    and player_stat.defending_duels_ground_won is not None
                ):
                    self.check_equal(
                        result,
                        "defending_duels_won == aerial_won + ground_won",
                        player_stat.defending_duels_won,
                        player_stat.defending_duels_aerial_won
                        + player_stat.defending_duels_ground_won,
                        entity_id,
                    )
                self.check_non_negative(
                    result,
                    "defending_interceptions >= 0",
                    player_stat.defending_interceptions,
                    entity_id,
                )
                self.check_non_negative(
                    result,
                    "defending_recoveries >= 0",
                    player_stat.defending_recoveries,
                    entity_id,
                )
                self.check_non_negative(
                    result,
                    "defending_blocked >= 0",
                    player_stat.defending_blocked,
                    entity_id,
                )

                self.check_lte(
                    result,
                    "goalkeeping_penalty_saved <= goalkeeping_penalties_faced",
                    player_stat.goalkeeping_penalty_saved,
                    player_stat.goalkeeping_penalties_faced,
                    entity_id,
                )
                self.check_lte(
                    result,
                    "goalkeeping_penalty_goals_conceded <= goalkeeping_penalties_faced",
                    player_stat.goalkeeping_penalty_goals_conceded,
                    player_stat.goalkeeping_penalties_faced,
                    entity_id,
                )
                if (
                    player_stat.goalkeeping_penalty_saved is not None
                    and player_stat.goalkeeping_penalty_goals_conceded is not None
                    and player_stat.goalkeeping_penalties_faced is not None
                ):
                    self.check_true(
                        result,
                        "goalkeeping_penalty_saved + conceded <= faced",
                        (
                            player_stat.goalkeeping_penalty_saved
                            + player_stat.goalkeeping_penalty_goals_conceded
                            <= player_stat.goalkeeping_penalties_faced
                        ),
                        entity_id,
                        detail=(
                            f"saved={player_stat.goalkeeping_penalty_saved}, "
                            f"conceded={player_stat.goalkeeping_penalty_goals_conceded}, "
                            f"faced={player_stat.goalkeeping_penalties_faced}"
                        ),
                    )
                self.check_non_negative(
                    result,
                    "goalkeeping_saves >= 0",
                    player_stat.goalkeeping_saves,
                    entity_id,
                )
                self.check_lte(
                    result,
                    "goalkeeping_clean_sheets <= appearances",
                    player_stat.goalkeeping_clean_sheets,
                    player_stat.appearances,
                    entity_id,
                )

                self.check_lte(
                    result,
                    "possession_dribble_successful <= possession_dribble_total",
                    player_stat.possession_dribble_successful,
                    player_stat.possession_dribble_total,
                    entity_id,
                )
                self.check_non_negative(
                    result,
                    "possession_touches >= 0",
                    player_stat.possession_touches,
                    entity_id,
                )
                self.check_lte(
                    result,
                    "possession_touches_in_opposition_box <= possession_touches",
                    player_stat.possession_touches_in_opposition_box,
                    player_stat.possession_touches,
                    entity_id,
                )

                self.check_non_negative(
                    result,
                    "discipline_yellow_cards >= 0",
                    player_stat.discipline_yellow_cards,
                    entity_id,
                )
                self.check_non_negative(
                    result,
                    "discipline_red_cards >= 0",
                    player_stat.discipline_red_cards,
                    entity_id,
                )
                self.check_lte(
                    result,
                    "discipline_red_cards_direct <= discipline_red_cards",
                    player_stat.discipline_red_cards_direct,
                    player_stat.discipline_red_cards,
                    entity_id,
                )
                self.check_lte(
                    result,
                    "discipline_red_cards <= appearances",
                    player_stat.discipline_red_cards,
                    player_stat.appearances,
                    entity_id,
                )

                self.check_true(
                    result,
                    "appearances <= team season match count",
                    player_stat.appearances
                    <= season_team_match_counts.get(
                        (player_stat.season_id, player_stat.team_id),
                        0,
                    ),
                    entity_id,
                    detail=(
                        f"appearances={player_stat.appearances}, "
                        f"team_matches={season_team_match_counts.get((player_stat.season_id, player_stat.team_id), 0)}"
                    ),
                )
                if player_stat.season_id not in seasons_with_pca:
                    result.add_skip(
                        "player registered in PlayerChampionshipAssociation",
                        entity_id,
                    )
                else:
                    self.check_true(
                        result,
                        "player registered in PlayerChampionshipAssociation",
                        player_stat.season_id
                        in player_season_memberships.get(player_stat.player_id, set()),
                        entity_id,
                        detail=f"season_id={player_stat.season_id}",
                    )
                if player_stat.season_id not in seasons_with_tca:
                    result.add_skip(
                        "team registered in TeamChampionshipAssociation",
                        entity_id,
                    )
                else:
                    self.check_true(
                        result,
                        "team registered in TeamChampionshipAssociation",
                        (player_stat.team_id, player_stat.season_id)
                        in team_season_memberships,
                        entity_id,
                        detail=f"season_id={player_stat.season_id}",
                    )

                self.check_fk_exists(
                    result,
                    "player_id FK",
                    player_stat.player_id,
                    player_ids,
                    entity_id,
                )
                self.check_fk_exists(
                    result,
                    "team_id FK",
                    player_stat.team_id,
                    team_ids,
                    entity_id,
                )
                self.check_fk_exists(
                    result,
                    "season_id FK",
                    player_stat.season_id,
                    season_fk_ids,
                    entity_id,
                )

        return result
