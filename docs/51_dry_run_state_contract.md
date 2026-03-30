# Dry-run state contract

This step integrates the exact-duplicate dry-run core into `QmlAppState` without changing `Main.qml` yet.

## Exposed properties
- `dryRunReady`
- `dryRunFilterKey`
- `dryRunFilterOptions`
- `dryRunPlannedCount`
- `dryRunBlockedCount`
- `dryRunDeleteCount`
- `dryRunExcludeFromCopyCount`
- `dryRunExcludeFromMoveCount`
- `dryRunStatusLabel`
- `dryRunRowsCountLabel`
- `dryRunRows`

## Exposed slot
- `setDryRunFilter(key)`

## Purpose
This gives the UI layer a stable contract for the next step: a dedicated dry-run page or stage with filters and an explicit table of planned vs blocked rows.
