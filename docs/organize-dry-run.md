# Organize Dry-Run v1

This document describes the first rebuilt organizer block in the core-first architecture.

## Goal

Turn scanned media files into a transparent organize plan without moving or copying anything yet.

## Current behavior

`media-manager organize` now builds a dry-run plan on top of:

1. scanner
2. metadata inspection
3. date resolver v1

For each discovered media file, the planner currently:

- resolves a capture datetime
- renders a relative target directory from a pattern
- keeps the original filename
- computes a target path under the chosen target root
- marks the row as planned, skipped, conflict, or error

## Supported pattern tokens

- `{year}`
- `{month}`
- `{day}`
- `{year_month}`
- `{year_month_day}`
- `{source_name}`

Default pattern:

```text
{year}/{year_month_day}
```

## Current safety rules

- no file operations are executed
- existing target paths are marked as conflicts
- duplicate target collisions inside the same dry-run are marked as conflicts
- files already located at their planned target path are marked as skipped

## Not in v1 yet

- rename-template integration
- unique-name collision solving
- state-backed idempotence
- apply mode
- copy/move execution engine
