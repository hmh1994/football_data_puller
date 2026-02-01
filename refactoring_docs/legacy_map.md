# Legacy Map: Pre-migration -> Post-migration

**Date**: 2026-02-01
**Snapshot**: `pre-migration/legacy-scripts-2026-01-26` tag

## Script Consolidation Strategy

`app.py` is the main entry point (stays at root). Legacy scripts archived to `archive/legacy_scripts/`.

## File Relocation

| Before | After | Integration | Status |
|--------|-------|-------------|--------|
| `app.py` | `app.py` (root, rewritten) | Main entry point (unified CLI) | Active |
| `football_data_manager/` | `archive/football_data_manager/` | Replaced by new 4-component architecture | Archived |
| `b.py` | `archive/legacy_scripts/ops_pulselive_and_analytics.py` | `app.py run` / `app.py pull-data {entity}` | Archived |
| `c.py` | `archive/legacy_scripts/backfill_player_stat_scores.py` | Auto-calculation | Archived |
| `a.py` | `archive/legacy_scripts/migrate_old_to_new_schema.py` | None | Non-functional |

## CLI Command Mapping

| Before | After | Function |
|--------|-------|----------|
| `python app.py health` | `python app.py health` | Build status & health check |
| `python b.py` (background) | `python app.py run` | Master process (cron scheduler) |
| `python b.py` (per entity) | `python app.py pull-data {entity}` | Specific entity data pulling |
| `python c.py` | (auto-execution) | Player analytics included in pull |
| `python a.py` | (unavailable) | Old schema migration |

**Entity examples**:

- `python app.py pull-data competition`
- `python app.py pull-data season`
- `python app.py pull-data team`
- `python app.py pull-data player`
- `python app.py pull-data match`

## Directory Layout

### Root - Main entry point
- `app.py`: Unified CLI providing all commands

### `archive/football_data_manager/` - Original codebase
- Full pre-refactoring codebase (entities, repositories, pullers, services)
- Preserved for reference during new 4-component architecture build
- Imports will NOT resolve from this location

### `archive/legacy_scripts/` - Backup and history
- Original scripts preserved (not executable)
- Logic consolidated into `app.py`

## Preserved Implementations

All business logic consolidated into `app.py`:

1. **Cron scheduling** (from `b.py`):
    - Command: `python app.py run`
    - Function: Master process startup, periodic data pulling schedule management
    - Source: `archive/legacy_scripts/ops_pulselive_and_analytics.py`

2. **Per-entity data pulling** (from `b.py`):
    - Command: `python app.py pull-data {entity}`
    - Function: Puller + Merger execution for specific entity
    - Docs: `refactoring_docs/3_calculation_formulas_reference.md` (Section 2, 3)
    - Source: `archive/legacy_scripts/ops_pulselive_and_analytics.py`

3. **Player stat scores** (from `c.py`):
    - Integration: Auto-execution during player analytics calculation
    - Docs: `refactoring_docs/3_calculation_formulas_reference.md` (Section 1)
    - Source: `archive/legacy_scripts/backfill_player_stat_scores.py`

## Rollback

```bash
# Full rollback
git reset --hard pre-migration/legacy-scripts-2026-01-26

# Single file restore
git show pre-migration/legacy-scripts-2026-01-26:c.py > c.py
```

## Future Refactoring (After Phase 0)

- Extract `app.py` logic into domain modules
- Keep CLI as a thin wrapper only
- Review `archive/legacy_scripts/` for eventual removal
