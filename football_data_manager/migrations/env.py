import asyncio
import os
import ssl
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Entity imports (new repository/entities/ path)
from football_data_manager.repository.entities.base import Base
from football_data_manager.repository.entities.analytics import AnalyticsEntity  # noqa: F401
from football_data_manager.repository.entities.awards import AwardEntity  # noqa: F401
from football_data_manager.repository.entities.competitions import CompetitionEntity  # noqa: F401
from football_data_manager.repository.entities.fixtures import FixtureEntity  # noqa: F401
from football_data_manager.repository.entities.grounds import GroundEntity  # noqa: F401
from football_data_manager.repository.entities.match_stats import MatchStatEntity  # noqa: F401
from football_data_manager.repository.entities.matches import MatchEntity  # noqa: F401
from football_data_manager.repository.entities.news import NewsEntity  # noqa: F401
from football_data_manager.repository.entities.officials import OfficialEntity  # noqa: F401
from football_data_manager.repository.entities.player_stats import PlayerStatEntity  # noqa: F401
from football_data_manager.repository.entities.players import PlayerEntity  # noqa: F401
from football_data_manager.repository.entities.seasons import SeasonEntity  # noqa: F401
from football_data_manager.repository.entities.staffs import StaffEntity  # noqa: F401
from football_data_manager.repository.entities.team_stats import TeamStatEntity  # noqa: F401
from football_data_manager.repository.entities.teams import TeamEntity  # noqa: F401

# Association imports (one class per file)
from football_data_manager.repository.entities.match_card_association import MatchCardAssociation  # noqa: F401
from football_data_manager.repository.entities.match_goal_association import MatchGoalAssociation  # noqa: F401
from football_data_manager.repository.entities.match_lineup_association import MatchLineupAssociation  # noqa: F401
from football_data_manager.repository.entities.match_substitute_association import MatchSubstituteAssociation  # noqa: F401
from football_data_manager.repository.entities.match_substitution_association import MatchSubstitutionAssociation  # noqa: F401
from football_data_manager.repository.entities.team_championship_association import TeamChampionshipAssociation  # noqa: F401
from football_data_manager.repository.entities.player_championship_association import PlayerChampionshipAssociation  # noqa: F401
from football_data_manager.repository.entities.staff_award_association import StaffAwardAssociation  # noqa: F401
from football_data_manager.repository.entities.news_team_association import NewsTeamAssociation  # noqa: F401
from football_data_manager.repository.entities.player_stat_award_association import PlayerStatAwardAssociation  # noqa: F401
from football_data_manager.repository.entities.team_stat_match_association import TeamStatMatchAssociation  # noqa: F401

# Alembic Config object
config = context.config

# Logging setup
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Entity metadata for autogenerate support
target_metadata = Base.metadata

# Tables to exclude from autogenerate (not managed by Alembic)
EXCLUDED_TABLES = {"metadata"}


def include_name(name: str, type_: str, parent_names: dict) -> bool:
    """Filter out tables that are not managed by Alembic."""
    if type_ == "table":
        return name not in EXCLUDED_TABLES
    return True


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
    return config_service.db.sqlalchemy_url.render_as_string(hide_password=False)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (SQL script generation only)."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_name=include_name,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_name=include_name,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode (actual DB application)."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args={"ssl": ssl_context},
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
