# Archive

Pre-refactoring code archived for reference. Not directly executable.

**Snapshot tag**: `pre-migration/legacy-scripts-2026-01-26`

---

## Contents

### `football_data_manager/`

**Archived**: 2026-02-01
**Purpose**: Complete pre-refactoring codebase (entities, repositories, pullers, services)

**Status**: Archived — imports will not resolve from this location

- `common/`: Repositories, entities, services (BaseRepository, DI containers, etc.)
- `puller/`: Puller services (pulselive, pulselive_new, the_athletic)

This is the full original codebase before restructuring into the new 4-component architecture
(Repository, Puller, Merger, Scheduler). Preserved for reference during refactoring.

### `legacy_scripts/`

**Archived**: 2026-02-01
**Purpose**: Root-level scripts (a.py, b.py, c.py) renamed and archived

See `legacy_scripts/README.md` for details.

---

## Restore from Git History

```bash
# View original state
git show pre-migration/legacy-scripts-2026-01-26:football_data_manager/
git show pre-migration/legacy-scripts-2026-01-26:a.py
git show pre-migration/legacy-scripts-2026-01-26:b.py
git show pre-migration/legacy-scripts-2026-01-26:c.py

# Full rollback
git reset --hard pre-migration/legacy-scripts-2026-01-26
```