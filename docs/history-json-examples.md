# Workflow history JSON examples

This document shows example shapes for the workflow history-related JSON outputs.

The goal is not to repeat every field definition from the tests, but to make it easier to reason about compatibility-sensitive output when changing CLI behavior.

## `workflow history --json`

Typical shape:

```json
{
  "path": "C:/runs",
  "command_filter": null,
  "record_type_filter": null,
  "only_successful": false,
  "only_failed": false,
  "only_apply_requested": false,
  "only_preview": false,
  "has_reversible_entries": null,
  "min_entry_count": null,
  "min_reversible_entry_count": null,
  "created_at_after": null,
  "created_at_before": null,
  "summary_only": false,
  "summary": {
    "entry_count": 2,
    "successful_count": 1,
    "failed_count": 1,
    "reversible_entry_count": 3,
    "entries_with_reversible_count": 1,
    "command_summary": {
      "organize": 1,
      "rename": 1
    },
    "record_type_summary": {
      "execution_journal": 1,
      "run_log": 1
    },
    "apply_summary": {
      "apply_requested": 1,
      "preview_only": 1
    },
    "exit_code_summary": {
      "0": 1,
      "2": 1
    },
    "latest_created_at_utc": "2026-04-18T10:00:00+00:00"
  },
  "entries": [
    {
      "path": "C:/runs/rename.json",
      "record_type": "run_log",
      "command_name": "rename",
      "apply_requested": false,
      "exit_code": 0,
      "created_at_utc": "2026-04-18T10:00:00+00:00",
      "entry_count": 2,
      "reversible_entry_count": 0,
      "successful": true,
      "has_reversible_entries": false
    }
  ]
}
```

Notes:

- `path` is the scanned root path.
- `entries` is either populated or empty when `--summary-only` is used.
- summary keys are compatibility-sensitive and should not be renamed lightly.

## `workflow last --json`

Typical successful shape:

```json
{
  "path": "C:/runs",
  "record_type": "run_log",
  "command_name": "rename",
  "apply_requested": false,
  "exit_code": 0,
  "created_at_utc": "2026-04-18T10:00:00+00:00",
  "entry_count": 2,
  "reversible_entry_count": 0,
  "successful": true,
  "has_reversible_entries": false,
  "entry": {
    "path": "C:/runs/rename.json",
    "record_type": "run_log",
    "command_name": "rename",
    "apply_requested": false,
    "exit_code": 0,
    "created_at_utc": "2026-04-18T10:00:00+00:00",
    "entry_count": 2,
    "reversible_entry_count": 0,
    "successful": true,
    "has_reversible_entries": false
  },
  "entry_path": "C:/runs/rename.json",
  "history_root_path": "C:/runs",
  "command_filter": "rename",
  "record_type_filter": null,
  "only_successful": false,
  "only_failed": false,
  "only_apply_requested": false,
  "only_preview": false,
  "has_reversible_entries": null,
  "min_entry_count": null,
  "min_reversible_entry_count": null,
  "created_at_after": null,
  "created_at_before": null
}
```

Compatibility notes:

- top-level fields like `command_name` must remain available for older callers
- the nested `entry` object is also expected by some regression tests
- `path` is the history root path, not the concrete entry file path
- `entry_path` carries the concrete matching file path

Typical no-match shape:

```json
{
  "path": "C:/runs",
  "command_filter": "rename",
  "record_type_filter": null,
  "only_successful": false,
  "only_failed": false,
  "only_apply_requested": false,
  "only_preview": false,
  "has_reversible_entries": null,
  "min_entry_count": null,
  "min_reversible_entry_count": null,
  "created_at_after": null,
  "created_at_before": null,
  "entry": null
}
```

## `workflow history-latest-by-command --json`

Typical shape:

```json
{
  "path": "C:/runs",
  "command_filter": null,
  "record_type_filter": null,
  "only_successful": false,
  "only_failed": false,
  "only_apply_requested": false,
  "only_preview": false,
  "has_reversible_entries": null,
  "min_entry_count": null,
  "min_reversible_entry_count": null,
  "created_at_after": null,
  "created_at_before": null,
  "summary_only": false,
  "summary": {
    "entry_count": 3,
    "successful_count": 2,
    "failed_count": 1,
    "reversible_entry_count": 3,
    "entries_with_reversible_count": 1,
    "command_summary": {
      "organize": 1,
      "rename": 1,
      "trip": 1
    },
    "record_type_summary": {
      "execution_journal": 1,
      "run_log": 2
    },
    "apply_summary": {
      "apply_requested": 2,
      "preview_only": 1
    },
    "exit_code_summary": {
      "0": 2,
      "3": 1
    },
    "latest_created_at_utc": "2026-04-18T13:00:00+00:00"
  },
  "entries": [
    {
      "path": "C:/runs/rename-new.json",
      "record_type": "run_log",
      "command_name": "rename",
      "apply_requested": false,
      "exit_code": 0,
      "created_at_utc": "2026-04-18T13:00:00+00:00",
      "entry_count": 2,
      "reversible_entry_count": 0,
      "successful": true,
      "has_reversible_entries": false
    }
  ]
}
```

This output is safest when treated as a specialized list command:

- same filter metadata conventions as `history`
- same entry payload shape as other history outputs
- summary describes the selected latest-per-command set, not the full raw directory
