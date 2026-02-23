from enum import StrEnum


class SyncEntity(StrEnum):
    """Supported sync targets."""

    COMPETITION = "competition"
    SEASON = "season"
    TEAM = "team"
    PLAYER = "player"
    FIXTURE = "fixture"
    MATCH = "match"
    MATCH_STAT = "match-stat"
    PLAYER_STAT = "player-stat"
    TEAM_STAT = "team-stat"
    AWARD = "award"
    NEWS = "news"


DEPENDENCY_GRAPH: dict[SyncEntity, list[SyncEntity]] = {
    SyncEntity.COMPETITION: [],
    SyncEntity.SEASON: [SyncEntity.COMPETITION],
    SyncEntity.TEAM: [SyncEntity.COMPETITION, SyncEntity.SEASON],
    SyncEntity.PLAYER: [SyncEntity.TEAM],
    SyncEntity.FIXTURE: [SyncEntity.SEASON, SyncEntity.TEAM],
    SyncEntity.MATCH: [SyncEntity.PLAYER, SyncEntity.FIXTURE],
    SyncEntity.MATCH_STAT: [SyncEntity.MATCH],
    SyncEntity.PLAYER_STAT: [SyncEntity.PLAYER],
    SyncEntity.TEAM_STAT: [SyncEntity.MATCH, SyncEntity.TEAM],
    SyncEntity.AWARD: [SyncEntity.MATCH, SyncEntity.PLAYER_STAT],
    SyncEntity.NEWS: [],
}


class DependencyResolver:
    """Resolve sync execution order from dependency graph."""

    @staticmethod
    def resolve(target: SyncEntity) -> list[SyncEntity]:
        """Return topologically sorted dependency chain for one target."""
        return DependencyResolver._topological_sort([target])

    @staticmethod
    def resolve_all() -> list[SyncEntity]:
        """Return topologically sorted order for every sync entity."""
        return DependencyResolver._topological_sort(list(SyncEntity))

    @staticmethod
    def depends_on(target: SyncEntity, dependency: SyncEntity) -> bool:
        """Return whether target transitively depends on dependency."""
        if target == dependency:
            return False
        return dependency in DependencyResolver.resolve(target)

    @staticmethod
    def _topological_sort(targets: list[SyncEntity]) -> list[SyncEntity]:
        graph = DEPENDENCY_GRAPH
        ordered: list[SyncEntity] = []
        temporary: set[SyncEntity] = set()
        permanent: set[SyncEntity] = set()

        def visit(node: SyncEntity) -> None:
            if node in permanent:
                return
            if node in temporary:
                raise ValueError(f"Dependency cycle detected at '{node.value}'")

            temporary.add(node)
            for dep in graph.get(node, []):
                visit(dep)
            temporary.remove(node)
            permanent.add(node)
            ordered.append(node)

        for target in targets:
            visit(target)

        return ordered
