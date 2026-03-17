#!/usr/bin/env python3
"""
Football Data Puller - Main CLI Entry Point

Usage:
    python app.py health                        # Health check
    python app.py run                           # Start master process (cron scheduler)
    python app.py pull-data {entity}            # Legacy pull command
    python app.py sync {entity} [OPTIONS]       # Sync entity with dependency resolution
    python app.py validate {entity} [OPTIONS]   # Validate stored data integrity
"""
import asyncio
import argparse
import logging
import sys


def health():
    """
    Health check: verify system status

    Checks:
    - Database connection
    - Required dependencies
    - Configuration validity
    """
    print("Running health check...")

    try:
        from football_data_manager.common.repositories import Base  # noqa: F401

        print("  Import check: OK")

        # TODO: Add database connection check (Phase 1+)
        # TODO: Add dependency checks (Phase 1+)

        print("System healthy!")
        return 0
    except Exception as e:
        print(f"Health check failed: {e}")
        return 1


def run():
    """
    Start master process with cron scheduler

    This will:
    1. Initialize APScheduler
    2. Schedule periodic data pulling jobs
    3. Run continuously in background

    Jobs will be scheduled based on:
    - Competition/Season: Daily
    - Team/Player: Every 6 hours
    - Match: Every hour during match days
    """
    print("Starting master process...")
    print("Initializing cron scheduler...")

    # TODO: Implement scheduler logic (Phase 4)
    # from apscheduler.schedulers.asyncio import AsyncIOScheduler
    # scheduler = AsyncIOScheduler()
    # scheduler.add_job(...)
    # scheduler.start()

    print("WARNING: Scheduler implementation pending (Phase 4)")
    print("For now, use: python app.py pull-data {entity}")
    return 0


def pull_data(entity: str):
    """
    Pull data for specific entity

    Args:
        entity: Entity name (competition, season, team, player, match)

    Process:
    1. Initialize appropriate Puller
    2. Fetch data from source
    3. Run Merger to update database
    4. Calculate analytics (if applicable)
    """
    valid_entities = ["competition", "season", "team", "player", "match"]

    if entity not in valid_entities:
        print(f"Invalid entity: {entity}")
        print(f"Valid entities: {', '.join(valid_entities)}")
        return 1

    print(f"Pulling data for entity: {entity}")

    # TODO: Implement puller logic (Phase 2-3)
    # Example:
    # if entity == 'player':
    #     from football_data_manager.puller.services import PlayerPuller
    #     puller = PlayerPuller()
    #     data = await puller.pull()
    #
    #     from football_data_manager.merger import PlayerMerger
    #     merger = PlayerMerger()
    #     await merger.merge(data)

    print(f"WARNING: Puller implementation pending (Phase 2-3)")
    print(f"Entity '{entity}' pulling logic not yet migrated from b.py")
    return 0


def _validate_sync_args(
    entity: str,
    competition_id: str | None,
    season_id: str | None,
) -> None:
    if entity == "competition":
        return
    if entity == "news":
        return
    if entity == "season":
        if not competition_id:
            raise ValueError("--competition-id is required for 'season'")
        return

    if not competition_id:
        raise ValueError(f"--competition-id is required for '{entity}'")
    if not season_id:
        raise ValueError(f"--season-id is required for '{entity}'")


async def sync_data(
    entity: str,
    competition_id: str | None,
    season_id: str | None,
    league_abbr: str,
) -> int:
    from football_data_manager.syncer.container import create_sync_container
    from football_data_manager.syncer.dependency import SyncEntity
    from football_data_manager.syncer.orchestrator import SyncOrchestrator

    _validate_sync_args(entity, competition_id, season_id)

    container = await create_sync_container(validate_connection=False)
    orchestrator = SyncOrchestrator(container)

    if entity == "all":
        results = await orchestrator.sync_all(
            competition_source_id=competition_id,
            season_source_id=season_id,
            league_abbr=league_abbr,
        )
    else:
        results = await orchestrator.sync(
            target=SyncEntity(entity),
            competition_source_id=competition_id,
            season_source_id=season_id,
            league_abbr=league_abbr,
        )

    orchestrator.print_summary(results)
    return 0 if all(result.success for result in results) else 1


async def validate_data(
    entity: str,
    season_id: str | None,
    competition_id: str | None,
    show_detail: bool,
    detail_level: str | None,
) -> int:
    from football_data_manager.validator.container import create_validator_container
    from football_data_manager.validator.orchestrator import (
        ValidateEntity,
        ValidationOrchestrator,
    )
    from football_data_manager.validator.validators.base import CheckLevel

    container = await create_validator_container()
    orchestrator = ValidationOrchestrator(container)

    if entity == "all":
        results = await orchestrator.validate_all(
            season_id=season_id,
            competition_id=competition_id,
        )
    else:
        results = await orchestrator.validate(
            target=ValidateEntity(entity),
            season_id=season_id,
            competition_id=competition_id,
        )

    orchestrator.print_summary(results)

    if show_detail:
        level = CheckLevel(detail_level) if detail_level else None
        orchestrator.print_detail(results, level=level)

    return 0 if all(result.success for result in results) else 1


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Football Data Puller - Main CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python app.py health                    # Check system health
  python app.py run                       # Start master process
  python app.py pull-data competition     # Pull competition data
  python app.py pull-data player          # Pull player data
  python app.py sync team --competition-id 1 --season-id 578
  python app.py sync all --competition-id 1 --season-id 578
  python app.py validate all --detail
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Health command
    subparsers.add_parser("health", help="Check system health")

    # Run command
    subparsers.add_parser("run", help="Start master process with scheduler")

    # Pull-data command
    pull_parser = subparsers.add_parser("pull-data", help="Pull specific entity data")
    pull_parser.add_argument(
        "entity", help="Entity name (competition, season, team, player, match)"
    )

    # Sync command
    sync_parser = subparsers.add_parser(
        "sync",
        help="Sync entity data with dependency resolution (Pull -> Merge -> DB)",
    )
    sync_parser.add_argument(
        "entity",
        choices=[
            "competition",
            "season",
            "team",
            "player",
            "fixture",
            "match",
            "match-stat",
            "player-stat",
            "team-stat",
            "award",
            "news",
            "all",
        ],
        help="Target entity to sync",
    )
    sync_parser.add_argument(
        "--competition-id",
        help="Pulselive competition source ID (e.g. 1)",
    )
    sync_parser.add_argument(
        "--season-id",
        help="Pulselive season source ID (e.g. 578)",
    )
    sync_parser.add_argument(
        "--league-abbr",
        default="EN_PR",
        help="League abbreviation for news sync (default: EN_PR)",
    )

    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate data integrity across entities",
    )
    validate_parser.add_argument(
        "entity",
        choices=[
            "competition",
            "season",
            "team-stat",
            "player-stat",
            "match",
            "match-stat",
            "fixture",
            "player",
            "analytics",
            "news",
            "award",
            "cross-dataset",
            "all",
        ],
        help="Target entity to validate",
    )
    validate_parser.add_argument(
        "--season-id",
        help="Limit validation to a specific season",
    )
    validate_parser.add_argument(
        "--competition-id",
        help="Limit validation to a specific competition",
    )
    validate_parser.add_argument(
        "--detail",
        action="store_true",
        help="Show detailed validation checks",
    )
    validate_parser.add_argument(
        "--detail-level",
        choices=["PASS", "FAIL", "WARNING"],
        help="Filter detailed checks by result level",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)-7s] %(name)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.getLogger("gql").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)

    # Route to appropriate handler
    if args.command == "health":
        return health()
    elif args.command == "run":
        return run()
    elif args.command == "pull-data":
        return pull_data(args.entity)
    elif args.command == "sync":
        try:
            return asyncio.run(
                sync_data(
                    entity=args.entity,
                    competition_id=args.competition_id,
                    season_id=args.season_id,
                    league_abbr=args.league_abbr,
                )
            )
        except ValueError as error:
            print(f"Error: {error}")
            return 1
    elif args.command == "validate":
        try:
            return asyncio.run(
                validate_data(
                    entity=args.entity,
                    season_id=args.season_id,
                    competition_id=args.competition_id,
                    show_detail=args.detail,
                    detail_level=args.detail_level,
                )
            )
        except ValueError as error:
            print(f"Error: {error}")
            return 1
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
