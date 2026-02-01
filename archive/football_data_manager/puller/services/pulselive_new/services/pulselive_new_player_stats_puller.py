from asyncio import gather

from httpx import HTTPStatusError

from football_data_manager.common.repositories.competitions.competition_entity import (
    CompetitionEntity,
)
from football_data_manager.common.repositories.player_stats.player_stat_entity import (
    PlayerStatEntity,
)
from football_data_manager.common.repositories.player_stats.player_stat_repository import (
    PlayerStatRepository,
)
from football_data_manager.common.repositories.players.player_entity import (
    PlayerEntity,
)
from football_data_manager.common.repositories.repository_container import (
    CommonRepositoryContainer,
)
from football_data_manager.common.repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.repositories.teams.team_entity import TeamEntity
from football_data_manager.common.repositories.teams.team_repository import (
    TeamRepository,
)
from football_data_manager.puller.services.pulselive_new.components.pulselive_new_webclient import (
    PulseliveNewWebclient,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_player_stats_response import (
    PulseliveNewPlayerStatsResponse,
)


class PulseliveNewPlayerStatsPuller:
    """
    Service for pulling player statistics data from PulseLive v2 API.

    Handles fetching player performance statistics for specific players, competitions
    and seasons, and persisting or updating player stat data in the database.
    Also retrieves player shirt numbers from v1 API.

    :ivar __player_stat_repository: Repository for player stat database operations
    :ivar __webclient: HTTP client for PulseLive API requests
    """

    __player_stat_repository: PlayerStatRepository
    __team_repository: TeamRepository
    __webclient: PulseliveNewWebclient

    def __init__(
        self,
        repository_container: CommonRepositoryContainer,
        pulselive_service: PulseliveNewWebclient,
    ):
        """
        Initialize the player stats puller.

        :param repository_container: Container with repository instances
        :param pulselive_service: HTTP client for PulseLive API
        """
        self.__player_stat_repository = repository_container.player_stat_repository()
        self.__team_repository = repository_container.team_repository()
        self.__webclient = pulselive_service

    async def pull_player_stats(
        self,
        player: PlayerEntity,
        competition: CompetitionEntity,
        season: SeasonEntity,
    ) -> PlayerStatEntity | None:
        """
        Pull player statistics for a specific player, competition and season.

        Retrieves comprehensive player performance statistics including goals,
        assists, appearances, and detailed performance metrics from the API,
        processes them and stores or updates in the database.

        :param player: Player entity to pull statistics for
        :param competition: Competition entity
        :param season: Season entity
        :returns: Player stat entity created or updated, or None if API call fails
        """
        if competition.id != season.competition_id:
            raise ValueError(
                f"Season {season.id} does not belong to competition {competition.id}"
            )

        try:
            # Get player shirt number from v1 API
            player_details, player_stats = await gather(
                self.__webclient.get_v1_player_details(
                    competition.source_id, season.season_source_id, player.source_id
                ),
                self.__webclient.get_v2_player_stats(
                    competition.source_id, season.season_source_id, player.source_id
                ),
            )
            shirt_number = player_details.shirt_num or 0
            team = await self.__team_repository.read_by_pulselive_id(
                player_details.current_team.id
            )
            if team is None:
                raise ValueError(
                    f"Team with ID {player_stats.player.current_team.id} not found"
                )
            # Process and create/update player stat
            return await self.__process_player_stats(
                player, season, team, shirt_number, player_stats.stats
            )

        except HTTPStatusError as e:
            print(f"Failed to fetch player stats for {player.display_name_en}: {e}")
            return None
        except Exception as e:
            raise RuntimeError(
                f"Error processing player stats for {player.display_name_en}: {e}"
            ) from e

    @staticmethod
    def _safe_int(value: int | float | None) -> int | None:
        """
        Safely convert a value to int, handling None and float values.

        :param value: Value to convert to int
        :returns: Converted integer value or None if input is None
        """
        if value is None:
            return None
        return int(value)

    async def __process_player_stats(
        self,
        player: PlayerEntity,
        season: SeasonEntity,
        team: TeamEntity,
        shirt_number: int,
        stats: PulseliveNewPlayerStatsResponse,
    ) -> PlayerStatEntity:
        """
        Process player statistics from API response into database entity.

        Converts API response object to player stat entity with proper field mapping
        and handles creation or update of existing records.

        :param player: Player entity associated with the statistics
        :param season: Season entity for which statistics are recorded
        :param team: Team entity the player belongs to
        :param shirt_number: Player's jersey number for the season
        :param stats: Player statistics response from API
        :returns: Created or updated player stat entity
        """
        # Create PlayerStatEntity with all mapped fields (with int conversion)
        player_stat_entity = PlayerStatEntity(
            number=shirt_number,
            player=player,
            season=season,
            team=team,
            appearances=self._safe_int(stats.appearances),
            defending_blocked=self._safe_int(stats.blocked_shots),
            defending_duels_aerial_total=self._safe_int(stats.aerial_duels),
            defending_duels_aerial_won=self._safe_int(stats.aerial_duels_won),
            defending_duels_ground_total=self._safe_int(stats.ground_duels),
            defending_duels_ground_won=self._safe_int(stats.ground_duels_won),
            defending_duels_total=self._safe_int(stats.duels),
            defending_duels_won=self._safe_int(stats.duels_won),
            defending_fouls_committed=self._safe_int(stats.total_fouls_conceded),
            defending_interceptions=self._safe_int(stats.interceptions),
            defending_possession_won_final_third=self._safe_int(
                stats.possession_won_final_third
            ),
            defending_recoveries=self._safe_int(stats.recoveries),
            defending_tackles_total=self._safe_int(stats.total_tackles),
            defending_tackles_won=self._safe_int(stats.tackles_won),
            discipline_red_cards=self._safe_int(stats.total_red_cards),
            discipline_red_cards_direct=self._safe_int(stats.straight_red_cards),
            discipline_yellow_cards=self._safe_int(stats.yellow_cards),
            goalkeeping_clean_sheets=self._safe_int(stats.clean_sheets),
            goalkeeping_goals_conceded=self._safe_int(stats.goals_conceded),
            goalkeeping_goals_prevented=(
                stats.expected_goals_on_target_conceded - stats.goals_conceded
                if stats.expected_goals_on_target_conceded is not None
                and stats.goals_conceded is not None
                else None
            ),
            goalkeeping_high_claim=self._safe_int(stats.catches),
            goalkeeping_penalties_faced=self._safe_int(stats.penalties_faced),
            goalkeeping_penalty_goals_conceded=self._safe_int(
                stats.penalty_goals_conceded
            ),
            goalkeeping_penalty_saved=self._safe_int(
                (stats.penalties_faced if stats.penalties_faced is not None else 0)
                - (
                    stats.penalty_goals_conceded
                    if stats.penalty_goals_conceded is not None
                    else 0
                )
                if stats.penalties_faced is not None
                or stats.penalty_goals_conceded is not None
                else None
            ),
            goalkeeping_saves=self._safe_int(stats.saves_made),
            passing_long_balls_accurate=self._safe_int(stats.successful_long_passes),
            passing_long_balls_total=self._safe_int(
                (
                    stats.successful_long_passes
                    if stats.successful_long_passes is not None
                    else 0
                )
                + (
                    stats.unsuccessful_long_passes
                    if stats.unsuccessful_long_passes is not None
                    else 0
                )
                if stats.successful_long_passes is not None
                or stats.unsuccessful_long_passes is not None
                else None
            ),
            passing_assists=self._safe_int(stats.goal_assists),
            passing_chances_created=self._safe_int(
                (stats.goal_assists if stats.goal_assists is not None else 0)
                + (
                    stats.key_passes_attempt_assists
                    if stats.key_passes_attempt_assists is not None
                    else 0
                )
                if stats.goal_assists is not None
                or stats.key_passes_attempt_assists is not None
                else None
            ),
            passing_expected_assists=stats.expected_assists,
            passing_passes_successful=self._safe_int(
                (
                    stats.successful_short_passes
                    if stats.successful_short_passes is not None
                    else 0
                )
                + (
                    stats.successful_long_passes
                    if stats.successful_long_passes is not None
                    else 0
                )
                if stats.successful_short_passes is not None
                or stats.successful_long_passes is not None
                else None
            ),
            passing_passes_total=self._safe_int(stats.total_passes),
            passing_crosses_successful=self._safe_int(
                stats.successful_crosses_and_corners
            ),
            passing_crosses_total=self._safe_int(
                (
                    stats.successful_crosses_and_corners
                    if stats.successful_crosses_and_corners is not None
                    else 0
                )
                + (
                    stats.unsuccessful_crosses_and_corners
                    if stats.unsuccessful_crosses_and_corners is not None
                    else 0
                )
                if stats.successful_crosses_and_corners is not None
                or stats.unsuccessful_crosses_and_corners is not None
                else None
            ),
            possession_dribble_total=self._safe_int(
                (
                    stats.successful_dribbles
                    if stats.successful_dribbles is not None
                    else 0
                )
                + (
                    stats.unsuccessful_dribbles
                    if stats.unsuccessful_dribbles is not None
                    else 0
                )
                if stats.successful_dribbles is not None
                or stats.unsuccessful_dribbles is not None
                else None
            ),
            possession_dribble_successful=self._safe_int(stats.successful_dribbles),
            possession_fouls_won=self._safe_int(stats.total_fouls_won),
            possession_touches=self._safe_int(stats.touches),
            possession_touches_in_opposition_box=self._safe_int(
                stats.total_touches_in_opposition_box
            ),
            shooting_expected_goals=stats.expected_goals,
            shooting_expected_goals_non_penalty=(
                stats.expected_goals
                - (
                    0.79
                    * (
                        stats.penalties_taken
                        if stats.penalties_taken is not None
                        else 0
                    )
                )
                if stats.expected_goals is not None
                else None
            ),
            shooting_expected_goals_on_target=stats.expected_goals_on_target,
            shooting_goals=self._safe_int(stats.goals),
            shooting_goals_penalty=self._safe_int(stats.penalty_goals),
            shooting_penalties_taken=self._safe_int(stats.penalties_taken),
            shooting_shots=self._safe_int(
                (stats.total_shots if stats.total_shots is not None else 0)
                + (stats.blocked_shots if stats.blocked_shots is not None else 0)
                if stats.total_shots is not None or stats.blocked_shots is not None
                else None
            ),
            shooting_shots_on_target=self._safe_int(stats.shots_on_target_inc_goals),
        )

        # Create or update player stat using repository
        return await self.__player_stat_repository.upsert_player_stat(
            player_stat_entity
        )
