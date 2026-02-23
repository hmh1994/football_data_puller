from football_data_manager.puller.interfaces.pulselive.v1_match import (
    MatchStatInfoResponse,
    V1MatchTeamStatResponse,
)
from football_data_manager.repository.entities.match_stats import MatchStatEntity
from football_data_manager.repository.entities.matches import MatchEntity
from football_data_manager.repository.entities.teams import TeamEntity
from football_data_manager.repository.repositories.match_stats import MatchStatRepository
from football_data_manager.repository.repositories.teams import TeamRepository


class MatchStatMerger:
    """Merge match team-stat payloads into match-stat entities."""

    def __init__(
        self,
        match_stat_repo: MatchStatRepository,
        team_repo: TeamRepository,
    ):
        self._match_stat_repo = match_stat_repo
        self._team_repo = team_repo

    async def merge(
        self,
        match: MatchEntity,
        response: list[V1MatchTeamStatResponse],
    ) -> list[MatchStatEntity]:
        """Create/update two team match-stat entities for one match."""
        home_team_stat, away_team_stat = self._split_home_away(response)

        home_team = await self._team_repo.get_by_pulselive_id(home_team_stat.teamId)
        away_team = await self._team_repo.get_by_pulselive_id(away_team_stat.teamId)
        if home_team is None or away_team is None:
            return []

        home_entity = self._build_entity(
            match=match,
            team=home_team,
            our=home_team_stat.stats,
            opponent=away_team_stat.stats,
        )
        away_entity = self._build_entity(
            match=match,
            team=away_team,
            our=away_team_stat.stats,
            opponent=home_team_stat.stats,
        )

        results: list[MatchStatEntity] = []
        for entity in [home_entity, away_entity]:
            source_id = entity.source_id
            existing = await self._match_stat_repo.get_by_pulselive_id(source_id)
            if existing is None:
                created = await self._match_stat_repo.create(entity)
                if created is not None:
                    results.append(created)
                continue

            self._copy_stat_fields(existing, entity)
            updated = await self._match_stat_repo.update(existing)
            results.append(updated)

        return results

    @staticmethod
    def _split_home_away(
        response: list[V1MatchTeamStatResponse],
    ) -> tuple[V1MatchTeamStatResponse, V1MatchTeamStatResponse]:
        home = next(item for item in response if item.side.lower() == "home")
        away = next(item for item in response if item.side.lower() == "away")
        return home, away

    @staticmethod
    def _build_entity(
        match: MatchEntity,
        team: TeamEntity,
        our: MatchStatInfoResponse,
        opponent: MatchStatInfoResponse,
    ) -> MatchStatEntity:
        duels_aerial_total = our.aerial_won + our.aerial_lost
        duels_total = our.duel_won + our.duel_lost

        return MatchStatEntity(
            big_chances=int(our.big_chance_scored + our.big_chance_missed),
            big_chances_missed=int(our.big_chance_missed),
            corners=int(our.corner_taken),
            defense_blocks=int(our.outfielder_block),
            defense_clearances=int(our.total_clearance),
            defense_interceptions=int(our.interception),
            defense_keeper_saves=int(our.saves),
            defense_tackles_total=int(our.total_tackle),
            defense_tackles_won=int(our.won_tackle),
            discipline_red_cards=int(our.total_red_card),
            discipline_yellow_cards=int(our.total_yel_card),
            duels_aerial_total=int(duels_aerial_total),
            duels_aerial_won=int(our.aerial_won),
            duels_dribbles_successful=int(our.won_contest),
            duels_dribbles_total=int(our.total_contest),
            duels_ground_total=int(duels_total - duels_aerial_total),
            duels_ground_won=int(our.duel_won - our.aerial_won),
            duels_total=int(duels_total),
            duels_won=int(our.duel_won),
            expected_goals=float(our.expected_goals),
            expected_goals_non_penalty=float(our.expected_goals - (opponent.penalty_faced * 0.79)),
            expected_goals_on_target=float(our.expected_goals_on_target),
            fouls_committed=int(our.fk_foul_lost),
            passes_accurate=int(our.accurate_pass),
            passes_accurate_crosses=int(our.accurate_cross),
            passes_accurate_long_balls=int(our.accurate_long_balls),
            passes_offsides=int(our.total_offside),
            passes_opposition_half=int(our.accurate_fwd_zone_pass - our.accurate_cross),
            passes_own_half=int(our.accurate_back_zone_pass),
            passes_throws=int(our.total_throws),
            passes_total=int(our.total_pass),
            passes_total_crosses=int(our.total_cross),
            passes_total_long_balls=int(our.total_long_balls),
            passes_touches_in_opposition_box=int(our.touches_in_opp_box),
            possession=float(our.possession_percentage),
            shots_blocked=int(our.blocked_scoring_att),
            shots_hit_woodwork=int(our.hit_woodwork),
            shots_inside_box=int(our.attempts_ibox),
            shots_off_target=int(our.shot_off_target),
            shots_on_target=int(our.ontarget_scoring_att),
            shots_outside_box=int(our.attempts_obox),
            shots_total=int(our.total_scoring_att),
            match=match,
            team=team,
        )

    @staticmethod
    def _copy_stat_fields(target: MatchStatEntity, source: MatchStatEntity) -> None:
        target.big_chances = source.big_chances
        target.big_chances_missed = source.big_chances_missed
        target.corners = source.corners
        target.defense_blocks = source.defense_blocks
        target.defense_clearances = source.defense_clearances
        target.defense_interceptions = source.defense_interceptions
        target.defense_keeper_saves = source.defense_keeper_saves
        target.defense_tackles_total = source.defense_tackles_total
        target.defense_tackles_won = source.defense_tackles_won
        target.discipline_red_cards = source.discipline_red_cards
        target.discipline_yellow_cards = source.discipline_yellow_cards
        target.duels_aerial_total = source.duels_aerial_total
        target.duels_aerial_won = source.duels_aerial_won
        target.duels_dribbles_successful = source.duels_dribbles_successful
        target.duels_dribbles_total = source.duels_dribbles_total
        target.duels_ground_total = source.duels_ground_total
        target.duels_ground_won = source.duels_ground_won
        target.duels_total = source.duels_total
        target.duels_won = source.duels_won
        target.expected_goals = source.expected_goals
        target.expected_goals_non_penalty = source.expected_goals_non_penalty
        target.expected_goals_on_target = source.expected_goals_on_target
        target.fouls_committed = source.fouls_committed
        target.passes_accurate = source.passes_accurate
        target.passes_accurate_crosses = source.passes_accurate_crosses
        target.passes_accurate_long_balls = source.passes_accurate_long_balls
        target.passes_offsides = source.passes_offsides
        target.passes_opposition_half = source.passes_opposition_half
        target.passes_own_half = source.passes_own_half
        target.passes_throws = source.passes_throws
        target.passes_total = source.passes_total
        target.passes_total_crosses = source.passes_total_crosses
        target.passes_total_long_balls = source.passes_total_long_balls
        target.passes_touches_in_opposition_box = source.passes_touches_in_opposition_box
        target.possession = source.possession
        target.shots_blocked = source.shots_blocked
        target.shots_hit_woodwork = source.shots_hit_woodwork
        target.shots_inside_box = source.shots_inside_box
        target.shots_off_target = source.shots_off_target
        target.shots_on_target = source.shots_on_target
        target.shots_outside_box = source.shots_outside_box
        target.shots_total = source.shots_total
