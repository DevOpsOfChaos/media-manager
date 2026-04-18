# Duplicate session/state cleanup v1

This update improves the exact-duplicate session flow without introducing a full database or journaling layer.

## Goals

- save richer session metadata
- explain why a saved session could or could not be restored
- expose session state in CLI output and JSON reports
- keep the workflow safe and predictable

## Session snapshot schema

Saved snapshots now include:

- `schema_version`
- `created_at_utc`
- `group_signature`
- `exact_group_count`
- `decision_count`
- `decisions`

Older snapshots remain loadable. Missing metadata is filled with safe defaults.

## Restore result states

Restoring a duplicate session can now produce one of these states:

- `not_requested`
- `missing`
- `matched`
- `mismatch`
- `error`

These states are meant for user-facing CLI feedback and machine-readable reports.

## Why a session may not restore

Typical reasons:

- the snapshot file does not exist
- the current exact duplicate groups no longer match the saved signature
- the snapshot file is unreadable or invalid JSON
- saved keep decisions no longer point to valid candidates in the current groups

## CLI additions

`media-manager duplicates` now supports:

- `--show-session`

When loading a session, the command can now print a clear restore summary and include the same information in the JSON report.

## Scope of this update

This is still a file-based session system, not a full state store.

Later work can build on this by adding:

- per-run history
- command journaling
- partial review progress
- unified state for organize, rename, duplicates, and workflows
