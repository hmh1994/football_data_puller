# Legacy Scripts Archive

**Warning**: These scripts are NOT directly executable.

---

## Migration History

All script logic has been consolidated into `app.py`.

### `migrate_old_to_new_schema.py`

**Original location**: `a.py` (root)
**Archived**: 2026-02-01
**Purpose**: Data migration from old repository schema to new schema

**Status**: Non-functional

- `old_repositories` import no longer exists
- Preserved for history reference only

### `ops_pulselive_and_analytics.py`

**Original location**: `b.py` (root)
**Archived**: 2026-02-01
**Purpose**: Data pulling orchestration and analytics calculation

**Status**: Archived

- Puller logic -> `app.py pull-data {entity}` command
- Cron scheduling -> `app.py run` command
- Reference: `refactoring_docs/3_calculation_formulas_reference.md` (Section 2, 3)

### `backfill_player_stat_scores.py`

**Original location**: `c.py` (root)
**Archived**: 2026-02-01
**Purpose**: Player performance score calculation

**Status**: Archived

- Logic will be integrated into analytics calculation
- Will execute automatically during `app.py pull-data player`
- Reference: `refactoring_docs/3_calculation_formulas_reference.md` (Section 1)

---

## Restore from Git History

```bash
# View original files
git show pre-migration/legacy-scripts-2026-01-26:a.py
git show pre-migration/legacy-scripts-2026-01-26:b.py
git show pre-migration/legacy-scripts-2026-01-26:c.py
```