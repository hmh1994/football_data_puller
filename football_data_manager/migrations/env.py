import asyncio
import os
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Entity imports (15 entities)
from football_data_manager.common.repositories import Base
from football_data_manager.common.repositories.analytics.analytics_entity import AnalyticsEntity  # noqa: F401
from football_data_manager.common.repositories.awards.award_entity import AwardEntity  # noqa: F401
from football_data_manager.common.repositories.competitions.competition_entity import CompetitionEntity  # noqa: F401
from football_data_manager.common.repositories.fixtures.fixture_entity import FixtureEntity  # noqa: F401
from football_data_manager.common.repositories.grounds.ground_entity import GroundEntity  # noqa: F401
from football_data_manager.common.repositories.match_stats.match_stat_entity import MatchStatEntity  # noqa: F401
from football_data_manager.common.repositories.matches.match_entity import MatchEntity  # noqa: F401
from football_data_manager.common.repositories.news.news_entity import NewsEntity  # noqa: F401
from football_data_manager.common.repositories.officials.official_entity import OfficialEntity  # noqa: F401
from football_data_manager.common.repositories.player_stats.player_stat_entity import PlayerStatEntity  # noqa: F401
from football_data_manager.common.repositories.players.player_entity import PlayerEntity  # noqa: F401
from football_data_manager.common.repositories.seasons.season_entity import SeasonEntity  # noqa: F401
from football_data_manager.common.repositories.staffs.staff_entity import StaffEntity  # noqa: F401
from football_data_manager.common.repositories.team_stats.team_stat_entity import TeamStatEntity  # noqa: F401
from football_data_manager.common.repositories.teams.team_entity import TeamEntity  # noqa: F401

# Association table imports (11 associations)
from football_data_manager.common.repositories.matches.match_card_association import MatchCardAssociation  # noqa: F401
from football_data_manager.common.repositories.matches.match_goal_association import MatchGoalAssociation  # noqa: F401
from football_data_manager.common.repositories.matches.match_lineup_association import MatchLineupAssociation  # noqa: F401
from football_data_manager.common.repositories.matches.match_substitute_association import MatchSubstituteAssociation  # noqa: F401
from football_data_manager.common.repositories.matches.match_substitution_association import MatchSubstitutionAssociation  # noqa: F401
from football_data_manager.common.repositories.news.news_team_association import NewsTeamAssociation  # noqa: F401
from football_data_manager.common.repositories.player_stats.player_stat_award_association import PlayerStatAwardAssociation  # noqa: F401
from football_data_manager.common.repositories.players.player_championship_association import PlayerChampionshipAssociation  # noqa: F401
from football_data_manager.common.repositories.staffs.staff_award_association import StaffAwardAssociation  # noqa: F401
from football_data_manager.common.repositories.team_stats.team_stat_match_association import TeamStatMatchAssociation  # noqa: F401
from football_data_manager.common.repositories.teams.team_championship_association import TeamChampionshipAssociation  # noqa: F401

# Alembic Config object
config = context.config

# Logging setup
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Entity metadata for autogenerate support
target_metadata = Base.metadata


def get_url() -> str:
    """Get database URL from environment variable or ConfigService."""
    # Environment variable takes priority
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url

    # Fall back to ConfigService
    from football_data_manager.common.services.config.config_service import ConfigService

    config_path = Path(os.getenv("CONFIG_PATH", "./configs/.env"))
    config_service = ConfigService(config_path=config_path)
    return str(config_service.db.sqlalchemy_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (SQL script generation only)."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode (actual DB application)."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Online mode entry point."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
