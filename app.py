#!/usr/bin/env python3
"""
Football Data Puller - Main CLI Entry Point

Usage:
    python app.py health                  # Health check
    python app.py run                     # Start master process (cron scheduler)
    python app.py pull-data {entity}      # Pull specific entity data
"""
import argparse
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
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Health command
    subparsers.add_parser("health", help="Check system health")

    # Run command
    subparsers.add_parser("run", help="Start master process with scheduler")

    # Pull-data command
    pull_parser = subparsers.add_parser(
        "pull-data", help="Pull specific entity data"
    )
    pull_parser.add_argument(
        "entity", help="Entity name (competition, season, team, player, match)"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate handler
    if args.command == "health":
        return health()
    elif args.command == "run":
        return run()
    elif args.command == "pull-data":
        return pull_data(args.entity)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())