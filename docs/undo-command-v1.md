# Undo command v1

This document describes the first undo command built on top of execution journals.

## Goal

Apply-capable commands can already write structured execution journals.

`media-manager undo` is the first command that consumes those journals and turns them
into a safe preview or a real rollback step.

## Current scope

The command currently supports journals written by:

- `media-manager organize --apply --journal ...`
- `media-manager rename --apply --journal ...`
- `media-manager trip --apply --journal ...`

## Command

```powershell
media-manager undo --journal run.json
```

This is a preview by default.

Use `--apply` to execute the recorded rollback actions.

## Supported undo actions

### `delete_target`

Used for:

- organize copy
- trip link
- trip copy

Undo behavior:

- preview: report that the target would be deleted
- apply: delete the recorded target path when it still exists

### `move_back`

Used for:

- organize move

Undo behavior:

- preview: report that the file would be moved back
- apply: move the recorded path from the current location back to the original location

### `rename_back`

Used for:

- rename apply

Undo behavior:

- preview: report that the file would be renamed back
- apply: move the recorded path from the renamed location back to the original path

## Safety behavior in v1

- non-reversible journal entries are skipped
- missing undo source paths are skipped instead of treated as fatal corruption
- existing undo target paths block the rollback and are reported as errors
- the command never guesses missing paths

## Important limitation

This is still journal-based rollback, not a full history engine.

It depends on having a valid execution journal from the original apply run.
