# Execution preview core

This step adds an execution-oriented model on top of the existing exact-duplicate dry run.

## Added module
- `src/media_manager/execution_plan.py`

## Exposed app state
- `executionReady`
- `executionExecutableCount`
- `executionDeferredCount`
- `executionBlockedCount`
- `executionDeleteCount`
- `executionModeLabel`
- `executionStatusLabel`
- `executionRowsCountLabel`
- `executionRows`

## Interpretation
- `filesystem_delete` = real delete candidate in delete mode
- `pipeline_exclusion` = duplicate will be excluded from later copy/move pipeline
- `blocked` = unresolved keep decision still blocks trustworthy execution planning

## Purpose
The next UI step can now show not only dry-run rows, but also a more execution-oriented table and counters.
