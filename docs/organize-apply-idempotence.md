# Organize Apply and First Idempotence Rules

## Scope

This milestone extends organize planning with:

- executable organize actions for copy and move modes
- a minimal idempotence rule for existing targets
- CLI support for `--apply`

## Current execution behavior

Planned entries may now be executed:

- `copy` mode copies files with metadata preservation via `shutil.copy2`
- `move` mode moves files via `shutil.move`

Entries already marked as `skipped`, `conflict`, or `error` are not executed.

## First idempotence rule

If the target path already exists and the source file has the **same file size**, the planner marks the entry as:

- `status = skipped`
- `reason = target already exists with matching file size`

This is intentionally conservative and simple.

It is not yet a full fingerprint-based identity check.
That can be added later once a stronger state layer or hash-assisted verification exists.

## Safety limits

The current apply implementation still avoids trying to be too clever:

- no overwrite mode
- no automatic conflict renaming
- no rollback/journal yet
- no hash-based identity check yet

## Why this step matters

This gives the project its first real organize execution path while still keeping the logic explicit and reviewable.

It also starts the transition from pure planning toward state-aware and rerun-safe behavior.
