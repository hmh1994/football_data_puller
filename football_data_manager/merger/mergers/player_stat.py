from asyncio import gather

import httpx

from football_data_manager.puller.pullers.pulselive.player import PlayerPuller
from football_data_manager.puller.pullers.pulselive.player_stat import PlayerStatPuller
from football_data_manager.repository.entities.competitions import CompetitionEntity
from football_data_manager.repository.entities.player_stats import PlayerStatEntity
from football_data_manager.repository.entities.players import PlayerEntity
from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.entities.teams import TeamEntity
from football_data_manager.repository.repositories.player_stats import PlayerStatRepository
from football_data_manager.repository.repositories.teams import TeamRepository


class PlayerStatMerger:
    """Merge player stat API responses into player-stat entities."""

    _STAT_FIELDS = [
        "number",
        "appearances",
        "defending_blocked",
        "defending_duels_aerial_total",
        "defending_duels_aerial_won",
        "defending_duels_ground_total",
        "defending_duels_ground_won",
        "defending_duels_total",
        "defending_duels_won",
        "defending_fouls_committed",
        "defending_interceptions",
        "defending_possession_won_final_third",
        "defending_recoveries",
        "defending_tackles_total",
        "defending_tackles_won",
        "discipline_red_cards",
        "discipline_red_cards_direct",
        "discipline_yellow_cards",
        "goalkeeping_clean_sheets",
        "goalkeeping_goals_conceded",
        "goalkeeping_goals_prevented",
        "goalkeeping_high_claim",
        "goalkeeping_penalties_faced",
        "goalkeeping_penalty_goals_conceded",
        "goalkeeping_penalty_saved",
        "goalkeeping_saves",
        "passing_assists",
        "passing_chances_created",
        "passing_crosses_successful",
        "passing_crosses_total",
        "passing_expected_assists",
        "passing_long_balls_accurate",
        "passing_long_balls_total",
        "passing_passes_successful",
        "passing_passes_total",
        "possession_dribble_successful",
        "possession_dribble_total",
        "possession_fouls_won",
        "possession_touches",
        "possession_touches_in_opposition_box",
        "shooting_expected_goals",
        "shooting_expected_goals_non_penalty",
        "shooting_expected_goals_on_target",
        "shooting_goals",
        "shooting_goals_penalty",
        "shooting_penalties_taken",
        "shooting_shots",
        "shooting_shots_on_target",
    ]

    def __init__(
        self,
        player_stat_repo: PlayerStatRepository,
        team_repo: TeamRepository,
        player_puller: PlayerPuller,
        player_stat_puller: PlayerStatPuller,
    ):
        self._player_stat_repo = player_stat_repo
        self._team_repo = team_repo
        self._player_puller = player_puller
        self._player_stat_puller = player_stat_puller

    async def merge(
        self,
        player: PlayerEntity,
        competition: CompetitionEntity,
        season: SeasonEntity,
    ) -> PlayerStatEntity | None:
        """Fetch v1/v2 player stat APIs, then create/update one player-stat entity."""
        if season.competition_id != competition.id:
            raise ValueError(
                f"Season {season.id} does not belong to competition {competition.id}"
            )

        try:
            player_details, player_stats = await gather(
                self._player_puller.pull_player_details(
                    competition.source_id,
                    season.source_id.split("_")[-1],
                    player.source_id,
                ),
                self._player_stat_puller.pull_player_stats(
                    competition.source_id,
                    season.source_id.split("_")[-1],
                    player.source_id,
                ),
            )
        except httpx.HTTPError:
            return None

        current_team = player_details.current_team
        if current_team is None:
            return None

        team = await self._team_repo.get_by_pulselive_id(str(current_team["id"]))
        if team is None:
            return None

        mapped = self._build_player_stat(
            player=player,
            season=season,
            team=team,
            shirt_number=player_details.shirt_num or 0,
            stats=player_stats.stats,
        )

        existing = await self._player_stat_repo.get_by_pulselive_id(mapped.source_id)
        if existing is None:
            return await self._player_stat_repo.create(mapped)

        self._copy_fields(existing, mapped)
        return await self._player_stat_repo.update(existing)

    def _build_player_stat(
        self,
        player: PlayerEntity,
        season: SeasonEntity,
        team: TeamEntity,
        shirt_number: int,
        stats: dict,
    ) -> PlayerStatEntity:
        """Map API dictionary and derived formulas into PlayerStatEntity."""
        successful_long_passes = self._to_int(stats.get("successful_long_passes"))
        unsuccessful_long_passes = self._to_int(stats.get("unsuccessful_long_passes"))
        goal_assists = self._to_int(stats.get("goal_assists"))
        key_passes = self._to_int(stats.get("key_passes_attempt_assists"))
        successful_short_passes = self._to_int(stats.get("successful_short_passes"))
        successful_crosses = self._to_int(stats.get("successful_crosses_and_corners"))
        unsuccessful_crosses = self._to_int(stats.get("unsuccessful_crosses_and_corners"))
        successful_dribbles = self._to_int(stats.get("successful_dribbles"))
        unsuccessful_dribbles = self._to_int(stats.get("unsuccessful_dribbles"))

        expected_goals = self._to_float(stats.get("expected_goals"))
        penalties_taken = self._to_float(stats.get("penalties_taken"))
        total_shots = self._to_int(stats.get("total_shots"))
        blocked_shots = self._to_int(stats.get("blocked_shots"))

        penalties_faced = self._to_int(stats.get("penalties_faced"))
        penalty_goals_conceded = self._to_int(stats.get("penalty_goals_conceded"))
        xgot_conceded = self._to_float(stats.get("expected_goals_on_target_conceded"))
        goals_conceded = self._to_int(stats.get("goals_conceded"))

        return PlayerStatEntity(
            number=shirt_number,
            player=player,
            season=season,
            team=team,
            appearances=self._to_int(stats.get("appearances")),
            defending_blocked=self._to_int(stats.get("blocked_shots")),
            defending_duels_aerial_total=self._to_int(stats.get("aerial_duels")),
            defending_duels_aerial_won=self._to_int(stats.get("aerial_duels_won")),
            defending_duels_ground_total=self._to_int(stats.get("ground_duels")),
            defending_duels_ground_won=self._to_int(stats.get("ground_duels_won")),
            defending_duels_total=self._to_int(stats.get("duels")),
            defending_duels_won=self._to_int(stats.get("duels_won")),
            defending_fouls_committed=self._to_int(stats.get("total_fouls_conceded")),
            defending_interceptions=self._to_int(stats.get("interceptions")),
            defending_possession_won_final_third=self._to_int(
                stats.get("possession_won_final_third")
            ),
            defending_recoveries=self._to_int(stats.get("recoveries")),
            defending_tackles_total=self._to_int(stats.get("total_tackles")),
            defending_tackles_won=self._to_int(stats.get("tackles_won")),
            discipline_red_cards=self._to_int(stats.get("total_red_cards")),
            discipline_red_cards_direct=self._to_int(stats.get("straight_red_cards")),
            discipline_yellow_cards=self._to_int(stats.get("yellow_cards")),
            goalkeeping_clean_sheets=self._to_int(stats.get("clean_sheets")),
            goalkeeping_goals_conceded=goals_conceded,
            goalkeeping_goals_prevented=(
                xgot_conceded - goals_conceded
                if xgot_conceded is not None and goals_conceded is not None
                else None
            ),
            goalkeeping_high_claim=self._to_int(stats.get("catches")),
            goalkeeping_penalties_faced=penalties_faced,
            goalkeeping_penalty_goals_conceded=penalty_goals_conceded,
            goalkeeping_penalty_saved=(
                penalties_faced - penalty_goals_conceded
                if penalties_faced is not None and penalty_goals_conceded is not None
                else None
            ),
            goalkeeping_saves=self._to_int(stats.get("saves_made")),
            passing_long_balls_accurate=successful_long_passes,
            passing_long_balls_total=(
                (successful_long_passes or 0) + (unsuccessful_long_passes or 0)
                if successful_long_passes is not None
                or unsuccessful_long_passes is not None
                else None
            ),
            passing_assists=goal_assists,
            passing_chances_created=(
                (goal_assists or 0) + (key_passes or 0)
                if goal_assists is not None or key_passes is not None
                else None
            ),
            passing_expected_assists=self._to_float(stats.get("expected_assists")),
            passing_passes_successful=(
                (successful_short_passes or 0) + (successful_long_passes or 0)
                if successful_short_passes is not None
                or successful_long_passes is not None
                else None
            ),
            passing_passes_total=self._to_int(stats.get("total_passes")),
            passing_crosses_successful=successful_crosses,
            passing_crosses_total=(
                (successful_crosses or 0) + (unsuccessful_crosses or 0)
                if successful_crosses is not None or unsuccessful_crosses is not None
                else None
            ),
            possession_dribble_total=(
                (successful_dribbles or 0) + (unsuccessful_dribbles or 0)
                if successful_dribbles is not None or unsuccessful_dribbles is not None
                else None
            ),
            possession_dribble_successful=successful_dribbles,
            possession_fouls_won=self._to_int(stats.get("total_fouls_won")),
            possession_touches=self._to_int(stats.get("touches")),
            possession_touches_in_opposition_box=self._to_int(
                stats.get("total_touches_in_opposition_box")
            ),
            shooting_expected_goals=expected_goals,
            shooting_expected_goals_non_penalty=(
                expected_goals - (0.79 * penalties_taken)
                if expected_goals is not None and penalties_taken is not None
                else None
            ),
            shooting_expected_goals_on_target=self._to_float(
                stats.get("expected_goals_on_target")
            ),
            shooting_goals=self._to_int(stats.get("goals")),
            shooting_goals_penalty=self._to_int(stats.get("penalty_goals")),
            shooting_penalties_taken=self._to_int(stats.get("penalties_taken")),
            shooting_shots=(
                (total_shots or 0) + (blocked_shots or 0)
                if total_shots is not None or blocked_shots is not None
                else None
            ),
            shooting_shots_on_target=self._to_int(stats.get("shots_on_target_inc_goals")),
        )

    def _copy_fields(self, target: PlayerStatEntity, source: PlayerStatEntity) -> None:
        for field_name in self._STAT_FIELDS:
            setattr(target, field_name, getattr(source, field_name))

    @staticmethod
    def _to_int(value: int | float | None) -> int | None:
        if value is None:
            return None
        return int(value)

    @staticmethod
    def _to_float(value: int | float | None) -> float | None:
        if value is None:
            return None
        return float(value)
