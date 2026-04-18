
# Rename Apply and Idempotence v1

This milestone adds real rename execution on top of the dry-run planner.

## What changed

- `media-manager rename --apply` now executes planned rename operations.
- Dry-run planning still happens first and remains the source of truth.
- Execution only acts on entries with `status = planned`.

## Execution behavior

The rename executor reports entries as:
- `renamed`
- `skipped`
- `conflict`
- `error`

Without `--apply`, the execution layer reports `preview-rename` actions.

## First idempotence rule

If a file already matches the rendered target name, it is marked as:

- `status = skipped`
- `reason = source file already matches the planned rename target`

This makes repeat runs safe for already renamed files.

## Current safety boundaries

- conflicts are not auto-resolved
- existing target names remain conflicts
- apply mode only renames entries that are already planned cleanly
