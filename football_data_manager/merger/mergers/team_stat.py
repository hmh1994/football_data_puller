from football_data_manager.common.enums.period_enum import PeriodEnum
from football_data_manager.puller.pullers.pulselive.team_stat import TeamStatPuller
from football_data_manager.repository.entities.competitions import CompetitionEntity
from football_data_manager.repository.entities.grounds import GroundEntity
from football_data_manager.repository.entities.matches import MatchEntity
from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.entities.team_stats import TeamStatEntity
from football_data_manager.repository.entities.teams import TeamEntity
from football_data_manager.repository.repositories.fixtures import FixtureRepository
from football_data_manager.repository.repositories.matches import MatchRepository
from football_data_manager.repository.repositories.team_stats import TeamStatRepository


class TeamStatMerger:
    """Merge team-season stats with 2-phase update (DB-derived + API stats)."""

    def __init__(
        self,
        team_stat_repo: TeamStatRepository,
        fixture_repo: FixtureRepository,
        match_repo: MatchRepository,
        team_stat_puller: TeamStatPuller,
    ):
        self._team_stat_repo = team_stat_repo
        self._fixture_repo = fixture_repo
        self._match_repo = match_repo
        self._team_stat_puller = team_stat_puller

    async def merge(
        self,
        team: TeamEntity,
        competition: CompetitionEntity,
        season: SeasonEntity,
        ground: GroundEntity | None,
    ) -> TeamStatEntity | None:
        """Create/update one team-stat row and its match associations."""
        if season.competition_id != competition.id:
            raise ValueError(
                f"Season {season.id} does not belong to competition {competition.id}"
            )

        source_id = TeamStatEntity.get_source_id(season, team)
        existing = await self._team_stat_repo.get_by_pulselive_id(source_id)
        if existing is None:
            team_stat = TeamStatEntity(ground=ground, season=season, team=team)
        else:
            team_stat = existing
            if team_stat.ground_id is None and ground is not None:
                team_stat.ground_id = ground.id
            self._reset_derived_phase_1_fields(team_stat)
            await self._team_stat_repo.clear_match_associations(team_stat)

        fixtures = await self._fixture_repo.get_by_team_on_season(season, team)
        for fixture in fixtures:
            match = await self._match_repo.get_by_fixture(fixture)
            if match is None or match.period != PeriodEnum.FULLTIME:
                continue

            team_stat = await self._team_stat_repo.append_match(
                team_stat=team_stat,
                match=match,
                kickoff_time=fixture.kickoff_time,
            )
            self._apply_match_result(team_stat, match)

        try:
            api_stats = await self._team_stat_puller.pull_team_stats(
                competition.source_id,
                season.source_id.split("_")[-1],
                team.source_id,
            )
            self._apply_api_stats(team_stat, api_stats.stats)
        except Exception:
            # Keep phase-1 derived table data even when API stats fail.
            pass

        if existing is None:
            return await self._team_stat_repo.create(team_stat)
        return await self._team_stat_repo.update(team_stat)

    @staticmethod
    def _apply_match_result(team_stat: TeamStatEntity, match: MatchEntity) -> None:
        is_home = match.home_team_id == team_stat.team_id
        goals_for = match.home_team_score if is_home else match.away_team_score
        goals_against = match.away_team_score if is_home else match.home_team_score

        team_stat.overall_matches += 1
        team_stat.overall_goals_for += goals_for
        team_stat.overall_goals_against += goals_against
        team_stat.overall_goals_difference = (
            team_stat.overall_goals_for - team_stat.overall_goals_against
        )

        if is_home:
            team_stat.home_matches += 1
            team_stat.home_goals_for += goals_for
            team_stat.home_goals_against += goals_against
            team_stat.home_goals_difference = (
                team_stat.home_goals_for - team_stat.home_goals_against
            )
        else:
            team_stat.away_matches += 1
            team_stat.away_goals_for += goals_for
            team_stat.away_goals_against += goals_against
            team_stat.away_goals_difference = (
                team_stat.away_goals_for - team_stat.away_goals_against
            )

        if goals_for > goals_against:
            points = 3
            team_stat.overall_matches_won += 1
            if is_home:
                team_stat.home_matches_won += 1
            else:
                team_stat.away_matches_won += 1
        elif goals_for < goals_against:
            points = 0
            team_stat.overall_matches_lost += 1
            if is_home:
                team_stat.home_matches_lost += 1
            else:
                team_stat.away_matches_lost += 1
        else:
            points = 1
            team_stat.overall_matches_drawn += 1
            if is_home:
                team_stat.home_matches_drawn += 1
            else:
                team_stat.away_matches_drawn += 1

        team_stat.overall_points += points
        if is_home:
            team_stat.home_points += points
        else:
            team_stat.away_points += points

        team_stat.overall_cumulative_points.append(team_stat.overall_points)
        team_stat.home_cumulative_points.append(team_stat.home_points)
        team_stat.away_cumulative_points.append(team_stat.away_points)

    @staticmethod
    def _apply_api_stats(team_stat: TeamStatEntity, stats: dict) -> None:
        successful_crosses = TeamStatMerger._to_int(stats.get("successful_crosses_and_corners"))
        unsuccessful_crosses = TeamStatMerger._to_int(stats.get("unsuccessful_crosses_and_corners"))
        successful_long_passes = TeamStatMerger._to_int(stats.get("successful_long_passes"))
        unsuccessful_long_passes = TeamStatMerger._to_int(stats.get("unsuccessful_long_passes"))
        successful_short_passes = TeamStatMerger._to_int(stats.get("successful_short_passes"))

        team_stat.overall_stat_attack_corners = TeamStatMerger._to_int(
            stats.get("corners_taken_incl_short_corners")
        )
        team_stat.overall_stat_attack_shots_on_target = TeamStatMerger._to_int(
            stats.get("shots_on_target_incl_goals")
        )
        team_stat.overall_stat_attack_total_shots = TeamStatMerger._to_int(
            stats.get("total_shots")
        )
        team_stat.overall_stat_attack_touches_in_opposition_box = TeamStatMerger._to_int(
            stats.get("touches_in_opp_box")
        )
        team_stat.overall_stat_attack_expected_assists = TeamStatMerger._to_float(
            stats.get("expected_assists")
        )
        team_stat.overall_stat_attack_expected_goals = TeamStatMerger._to_float(
            stats.get("expected_goals")
        )
        team_stat.overall_stat_average_possession = TeamStatMerger._to_float(
            stats.get("possession_percentage")
        )

        team_stat.overall_stat_defense_blocks = TeamStatMerger._to_int(stats.get("blocked_shots"))
        team_stat.overall_stat_defense_clean_sheets = TeamStatMerger._to_int(
            stats.get("clean_sheets")
        )
        team_stat.overall_stat_defense_clearances = TeamStatMerger._to_int(
            stats.get("total_clearances")
        )
        team_stat.overall_stat_defense_interceptions = TeamStatMerger._to_int(
            stats.get("interceptions")
        )
        team_stat.overall_stat_defense_saves_penalty = TeamStatMerger._to_int(
            stats.get("penalties_saved")
        )
        team_stat.overall_stat_defense_tackles = TeamStatMerger._to_int(
            stats.get("times_tackled")
        )
        team_stat.overall_stat_defense_tackles_successful = TeamStatMerger._to_int(
            stats.get("tackles_won")
        )

        team_stat.overall_stat_discipline_fouls = TeamStatMerger._to_int(
            stats.get("total_fouls_conceded")
        )
        team_stat.overall_stat_discipline_red_cards = TeamStatMerger._to_int(
            stats.get("total_red_cards")
        )
        team_stat.overall_stat_discipline_red_cards_direct = TeamStatMerger._to_int(
            stats.get("straight_red_cards")
        )
        team_stat.overall_stat_discipline_yellow_cards = TeamStatMerger._to_int(
            stats.get("yellow_cards")
        )

        team_stat.overall_stat_attack_passes = TeamStatMerger._to_int(stats.get("total_passes"))
        team_stat.overall_stat_attack_passes_successful = TeamStatMerger._sum_optional(
            successful_long_passes,
            successful_short_passes,
        )
        team_stat.overall_stat_attack_crosses_successful = successful_crosses
        team_stat.overall_stat_attack_crosses = TeamStatMerger._sum_optional(
            successful_crosses,
            unsuccessful_crosses,
        )
        team_stat.overall_stat_attack_long_balls_successful = successful_long_passes
        team_stat.overall_stat_attack_long_balls = TeamStatMerger._sum_optional(
            successful_long_passes,
            unsuccessful_long_passes,
        )

        team_stat.overall_stat_defense_duels_total = TeamStatMerger._to_int(stats.get("duels"))
        team_stat.overall_stat_defense_duels_won = TeamStatMerger._to_int(stats.get("duels_won"))
        team_stat.overall_stat_defense_duels_aerial_total = TeamStatMerger._to_int(
            stats.get("aerial_duels")
        )
        team_stat.overall_stat_defense_duels_aerial_won = TeamStatMerger._to_int(
            stats.get("aerial_duels_won")
        )
        team_stat.overall_stat_defense_duels_ground_total = TeamStatMerger._to_int(
            stats.get("ground_duels")
        )
        team_stat.overall_stat_defense_duels_ground_won = TeamStatMerger._to_int(
            stats.get("ground_duels_won")
        )

        shots_conceded_inside = TeamStatMerger._to_int(stats.get("shots_on_conceded_inside_box"))
        shots_conceded_outside = TeamStatMerger._to_int(
            stats.get("shots_on_conceded_outside_box")
        )
        goals_conceded = TeamStatMerger._to_int(stats.get("goals_conceded"))
        penalties_saved = TeamStatMerger._to_int(stats.get("penalties_saved"))

        if (
            shots_conceded_inside is not None
            or shots_conceded_outside is not None
            or goals_conceded is not None
            or penalties_saved is not None
        ):
            team_stat.overall_stat_defense_saves = (
                (shots_conceded_inside or 0)
                + (shots_conceded_outside or 0)
                - (goals_conceded or 0)
                + (penalties_saved or 0)
            )

    @staticmethod
    def _reset_derived_phase_1_fields(team_stat: TeamStatEntity) -> None:
        team_stat.overall_matches = 0
        team_stat.overall_matches_won = 0
        team_stat.overall_matches_drawn = 0
        team_stat.overall_matches_lost = 0
        team_stat.overall_goals_for = 0
        team_stat.overall_goals_against = 0
        team_stat.overall_goals_difference = 0
        team_stat.overall_points = 0
        team_stat.overall_cumulative_points = []

        team_stat.home_matches = 0
        team_stat.home_matches_won = 0
        team_stat.home_matches_drawn = 0
        team_stat.home_matches_lost = 0
        team_stat.home_goals_for = 0
        team_stat.home_goals_against = 0
        team_stat.home_goals_difference = 0
        team_stat.home_points = 0
        team_stat.home_cumulative_points = []

        team_stat.away_matches = 0
        team_stat.away_matches_won = 0
        team_stat.away_matches_drawn = 0
        team_stat.away_matches_lost = 0
        team_stat.away_goals_for = 0
        team_stat.away_goals_against = 0
        team_stat.away_goals_difference = 0
        team_stat.away_points = 0
        team_stat.away_cumulative_points = []

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

    @staticmethod
    def _sum_optional(a: int | None, b: int | None) -> int | None:
        if a is None and b is None:
            return None
        return (a or 0) + (b or 0)
