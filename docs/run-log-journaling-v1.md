# Run log / journaling v1

This milestone adds a first lightweight journaling layer for the rebuilt CLI.

## Scope

The current implementation is intentionally small:

- no database
- no cross-run reconciliation
- no undo engine
- no long-lived state store yet

Instead, the goal is to make organize and rename runs reproducible and inspectable.

## New option

Both commands now support:

- `--run-log <path>`

This writes a structured JSON file with:

- schema version
- command name
- whether apply mode was requested
- exit code
- UTC timestamp
- the same payload shape that the command already uses for its JSON output

## Why this matters

This is the first useful state boundary for later work such as:

- journaling
- history views
- replay / comparison
- future undo preparation
- workflow reports

## Current commands

### Organize

```powershell
media-manager organize --source C:\Photos --target C:\Library --run-log logs\organize.json
```

### Rename

```powershell
media-manager rename --source C:\Photos --run-log logs\rename.json
```

## Future direction

Later milestones can build on this by adding:

- per-run IDs
- append-only history folders
- operation manifests
- true journaling for destructive actions
- undo metadata
