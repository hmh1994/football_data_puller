import math

from football_data_manager.common.enums.position_enum import PositionEnum
from football_data_manager.repository.entities.player_stats import PlayerStatEntity


class PlayerStatScorer:
    """Calculate category and overall scores for player-season statistics."""

    PRIOR_MINUTES = 450.0
    OVERALL_PRIOR_MINUTES = 225.0
    PRIOR_MEAN = 0.5
    OVERALL_GEOMETRIC_LAMBDA = 0.3

    POSITION_WEIGHTS = {
        PositionEnum.FORWARD: (0.35, 0.20, 0.05, 0.30, 0.10),
        PositionEnum.MIDFIELDER: (0.20, 0.35, 0.15, 0.20, 0.10),
        PositionEnum.DEFENDER: (0.05, 0.20, 0.45, 0.10, 0.20),
        PositionEnum.GOALKEEPER: (0.00, 0.10, 0.80, 0.00, 0.10),
        PositionEnum.UNKNOWN: (0.20, 0.25, 0.25, 0.15, 0.15),
    }

    def score(
        self,
        player_stat: PlayerStatEntity,
        position: PositionEnum,
    ) -> PlayerStatEntity:
        """Calculate and assign score fields on the given PlayerStatEntity."""
        shooting = self._score_shooting(player_stat)
        passing = self._score_passing(player_stat)
        defending = self._score_defending(player_stat, position)
        dribbling = self._score_dribbling(player_stat)
        discipline = self._score_discipline(player_stat)

        overall = self._score_overall(
            minutes=float(player_stat.minutes_played or 0),
            position=position,
            shooting=shooting,
            passing=passing,
            defending=defending,
            dribbling=dribbling,
            discipline=discipline,
        )

        player_stat.score_shooting = shooting
        player_stat.score_passing = passing
        player_stat.score_defending = defending
        player_stat.score_dribbling = dribbling
        player_stat.score_discipline = discipline
        player_stat.score_overall = overall
        return player_stat

    def _score_shooting(self, ps: PlayerStatEntity) -> float:
        minutes = float(ps.minutes_played or 0)
        if minutes <= 0:
            return 0.0

        npg = max(float(ps.shooting_goals or 0) - float(ps.shooting_goals_penalty or 0), 0.0)
        npxg = float(ps.shooting_expected_goals_non_penalty or 0)
        shots = float(ps.shooting_shots or 0)
        sot = float(ps.shooting_shots_on_target or 0)

        f_npxg_90 = self._norm01(self._per90(npxg, minutes), 0.0, 0.60)
        f_goals_90 = self._norm01(self._per90(npg, minutes), 0.0, 0.60)
        f_sot_rate = self._norm01(self._safe_div(sot, shots), 0.20, 0.60)
        f_gxg_ratio = self._norm01(self._safe_div(npg, npxg), 0.60, 1.40)

        raw = (
            0.40 * f_npxg_90
            + 0.30 * f_goals_90
            + 0.20 * f_sot_rate
            + 0.10 * f_gxg_ratio
        )
        shrunk = self._shrink(raw, self.PRIOR_MEAN, minutes, self.PRIOR_MINUTES)
        return self._to_score_100(shrunk)

    def _score_passing(self, ps: PlayerStatEntity) -> float:
        minutes = float(ps.minutes_played or 0)
        if minutes <= 0:
            return 0.0

        xa = float(ps.passing_expected_assists or 0)
        chances = float(ps.passing_chances_created or 0)
        assists = float(ps.passing_assists or 0)
        pass_success = float(ps.passing_passes_successful or 0)
        pass_total = float(ps.passing_passes_total or 0)
        cross_success = float(ps.passing_crosses_successful or 0)
        cross_total = float(ps.passing_crosses_total or 0)
        long_success = float(ps.passing_long_balls_accurate or 0)
        long_total = float(ps.passing_long_balls_total or 0)

        f_xa_90 = self._norm01(self._per90(xa, minutes), 0.0, 0.30)
        f_chances_90 = self._norm01(self._per90(chances, minutes), 0.0, 1.50)
        f_assists_90 = self._norm01(self._per90(assists, minutes), 0.0, 0.60)
        f_pass_accuracy = self._norm01(self._safe_div(pass_success, pass_total), 0.60, 0.95)
        f_cross_long_accuracy = self._norm01(
            0.5 * self._safe_div(cross_success, cross_total)
            + 0.5 * self._safe_div(long_success, long_total),
            0.20,
            0.75,
        )

        raw = (
            0.30 * f_xa_90
            + 0.20 * f_chances_90
            + 0.15 * f_assists_90
            + 0.25 * f_pass_accuracy
            + 0.10 * f_cross_long_accuracy
        )
        shrunk = self._shrink(raw, self.PRIOR_MEAN, minutes, self.PRIOR_MINUTES)
        return self._to_score_100(shrunk)

    def _score_defending(self, ps: PlayerStatEntity, position: PositionEnum) -> float:
        minutes = float(ps.minutes_played or 0)
        if minutes <= 0:
            return 0.0

        if position == PositionEnum.GOALKEEPER:
            saves_90 = self._norm01(self._per90(float(ps.goalkeeping_saves or 0), minutes), 0.0, 5.0)
            prevented_90 = self._norm01(
                self._per90(float(ps.goalkeeping_goals_prevented or 0), minutes),
                -1.0,
                1.0,
            )
            clean_sheet_90 = self._norm01(
                self._per90(float(ps.goalkeeping_clean_sheets or 0), minutes),
                0.0,
                0.5,
            )
            raw = 0.55 * saves_90 + 0.25 * prevented_90 + 0.20 * clean_sheet_90
            shrunk = self._shrink(raw, self.PRIOR_MEAN, minutes, self.PRIOR_MINUTES)
            return self._to_score_100(shrunk)

        tackles_90 = self._norm01(
            self._per90(float(ps.defending_tackles_won or 0), minutes),
            0.0,
            3.0,
        )
        interceptions_90 = self._norm01(
            self._per90(float(ps.defending_interceptions or 0), minutes),
            0.0,
            3.0,
        )
        blocked_90 = self._norm01(
            self._per90(float(ps.defending_blocked or 0), minutes),
            0.0,
            2.5,
        )
        recoveries_90 = self._norm01(
            self._per90(float(ps.defending_recoveries or 0), minutes),
            0.0,
            12.0,
        )
        duel_win = self._norm01(
            self._safe_div(
                float(ps.defending_duels_won or 0),
                float(ps.defending_duels_total or 0),
            ),
            0.40,
            0.75,
        )
        aerial_win = self._norm01(
            self._safe_div(
                float(ps.defending_duels_aerial_won or 0),
                float(ps.defending_duels_aerial_total or 0),
            ),
            0.35,
            0.80,
        )
        fouls_penalty = 1.0 - self._norm01(
            self._per90(float(ps.defending_fouls_committed or 0), minutes),
            0.3,
            2.5,
        )

        raw = (
            0.20 * tackles_90
            + 0.20 * interceptions_90
            + 0.10 * blocked_90
            + 0.15 * recoveries_90
            + 0.15 * duel_win
            + 0.10 * aerial_win
            + 0.10 * fouls_penalty
        )
        shrunk = self._shrink(raw, self.PRIOR_MEAN, minutes, self.PRIOR_MINUTES)
        return self._to_score_100(shrunk)

    def _score_dribbling(self, ps: PlayerStatEntity) -> float:
        minutes = float(ps.minutes_played or 0)
        if minutes <= 0:
            return 0.0

        dribble_success = float(ps.possession_dribble_successful or 0)
        dribble_total = float(ps.possession_dribble_total or 0)

        success_rate = self._norm01(self._safe_div(dribble_success, dribble_total), 0.30, 0.75)
        volume_90 = self._norm01(self._per90(dribble_total, minutes), 0.0, 6.0)
        fouls_won_90 = self._norm01(self._per90(float(ps.possession_fouls_won or 0), minutes), 0.0, 3.0)
        box_touches_90 = self._norm01(
            self._per90(float(ps.possession_touches_in_opposition_box or 0), minutes),
            0.0,
            10.0,
        )

        raw = (
            0.35 * success_rate
            + 0.30 * volume_90
            + 0.20 * fouls_won_90
            + 0.15 * box_touches_90
        )
        shrunk = self._shrink(raw, self.PRIOR_MEAN, minutes, self.PRIOR_MINUTES)
        return self._to_score_100(shrunk)

    def _score_discipline(self, ps: PlayerStatEntity) -> float:
        minutes = float(ps.minutes_played or 0)
        if minutes <= 0:
            return 0.0

        yellow = float(ps.discipline_yellow_cards or 0)
        red = float(ps.discipline_red_cards or 0)
        red_direct = float(ps.discipline_red_cards_direct or 0)
        fouls = float(ps.defending_fouls_committed or 0)

        weighted_cards = yellow + 2.0 * max(red - red_direct, 0.0) + 3.0 * red_direct
        cards_90 = self._norm01(self._per90(weighted_cards, minutes), 0.0, 2.0)
        fouls_90 = self._norm01(self._per90(fouls, minutes), 0.0, 3.0)

        penalty = 0.7 * cards_90 + 0.3 * fouls_90
        raw = 1.0 - self._clamp(penalty, 0.0, 1.0)
        shrunk = self._shrink(raw, self.PRIOR_MEAN, minutes, self.PRIOR_MINUTES)
        return self._to_score_100(shrunk)

    def _score_overall(
        self,
        minutes: float,
        position: PositionEnum,
        shooting: float,
        passing: float,
        defending: float,
        dribbling: float,
        discipline: float,
    ) -> float:
        if minutes <= 0:
            return 0.0

        weights = self.POSITION_WEIGHTS.get(position, self.POSITION_WEIGHTS[PositionEnum.UNKNOWN])
        sections = [
            shooting / 100.0,
            passing / 100.0,
            defending / 100.0,
            dribbling / 100.0,
            discipline / 100.0,
        ]

        arithmetic_mean = sum(weight * value for weight, value in zip(weights, sections))
        geometric_mean = math.exp(
            sum(weight * math.log(max(value, 1e-6)) for weight, value in zip(weights, sections))
        )
        blended = (1.0 - self.OVERALL_GEOMETRIC_LAMBDA) * arithmetic_mean + (
            self.OVERALL_GEOMETRIC_LAMBDA * geometric_mean
        )

        shrunk = self._shrink(
            blended,
            self.PRIOR_MEAN,
            minutes,
            self.OVERALL_PRIOR_MINUTES,
        )
        return self._to_score_100(shrunk)

    @staticmethod
    def _per90(value: float, minutes: float) -> float:
        return 90.0 * value / max(minutes, 1.0)

    @staticmethod
    def _safe_div(numerator: float, denominator: float) -> float:
        return numerator / max(denominator, 1e-9)

    @staticmethod
    def _shrink(raw: float, prior: float, sample: float, prior_sample: float) -> float:
        return (sample * raw + prior_sample * prior) / (sample + prior_sample)

    @staticmethod
    def _norm01(value: float, lower: float, upper: float) -> float:
        if upper <= lower:
            return 0.0
        return PlayerStatScorer._clamp((value - lower) / (upper - lower), 0.0, 1.0)

    @staticmethod
    def _clamp(value: float, lower: float, upper: float) -> float:
        return min(max(value, lower), upper)

    @staticmethod
    def _to_score_100(value_0_1: float) -> float:
        return round(100.0 * PlayerStatScorer._clamp(value_0_1, 0.0, 1.0), 2)
