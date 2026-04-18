# Execution journal v1

This document describes the first execution-journal layer for apply-capable commands.

## Goal

Run logs already capture high-level command payloads.

Execution journals add a second, narrower record:
they focus on the concrete file-system actions that were actually performed during an apply run.

This is the basis for future undo helpers.

## Current scope

Execution journals are currently supported for:

- `media-manager organize --apply`
- `media-manager rename --apply`
- `media-manager trip --apply`

## CLI option

Each supported command accepts:

```powershell
--journal <path>
```

The path is only meaningful together with `--apply`.

## Journal structure

The JSON file includes:

- `schema_version`
- `journal_type`
- `command_name`
- `apply_requested`
- `exit_code`
- `created_at_utc`
- `entry_count`
- `reversible_entry_count`
- `entries`

Each entry includes:

- `source_path`
- `target_path`
- `outcome`
- `reason`
- `reversible`
- `undo_action`
- `undo_from_path`
- `undo_to_path`

## Undo semantics in v1

### organize

- `copied` -> `delete_target`
- `moved` -> `move_back`

### rename

- `renamed` -> `rename_back`

### trip

- `linked` -> `delete_target`
- `copied` -> `delete_target`

## Important limitation

This is not a full undo engine yet.

The journal records the information that a later undo command will need,
but it does not execute rollback by itself yet.
