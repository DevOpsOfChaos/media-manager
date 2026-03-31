# Duplicate delete execution now goes to trash

This step changes the exact-duplicate delete runner from hard deletion to trash-based deletion.

## Changed module
- `src/media_manager/execution_runner.py`

## New behavior
When an exact-duplicate delete row is actually applied:
- the file is sent to the system trash via `send2trash`
- it is no longer removed immediately via `Path.unlink()`

## Preview behavior
Preview mode still does not touch the file system.
It now reports the outcome as `preview-trash` instead of `preview-delete`.

## Applied behavior
Real execution now reports the outcome as `trashed` instead of `deleted`.

## Why this matters
The project already grew a much more serious duplicate execution path.
Keeping hard deletes at this stage would be reckless.

Trash-based deletion is a safer default because it gives the user a recovery window while the broader execution UX is still evolving.
