# Workflow history filtering and audit notes

The workflow history layer can be used to inspect command run logs and execution journals after repeated CLI work.

## What history records capture

Recognized history records include:

- run logs
- execution journals

Each summarized history entry exposes:

- command name
- whether apply mode was requested
- exit code
- created timestamp in UTC
- total entry count
- reversible entry count

## Additive filter surface

The core history helpers support additive filtering for audit-focused workflows.

Examples of useful filters:

- command name
- record type
- only successful runs
- only failed runs
- only apply-requested runs
- only preview runs
- require reversible entries
- minimum total entry count
- minimum reversible entry count
- created-at lower bound
- created-at upper bound

## Why this matters

This makes it easier to answer practical questions like:

- show only failed duplicate preview runs
- find the newest successful apply journal for organize
- inspect only runs that actually produced reversible actions
- focus on larger runs instead of one-file smoke tests

## Example audit questions

- Which `organize` runs were successful and used apply mode?
- What is the latest `trip` execution journal with reversible entries?
- Which history records are preview-only failures?
- Which runs had at least 10 planned or executed entries?

## Core helper layers

The current history core is now broad enough to support multiple audit views without re-implementing filter logic.

### Single-entry helpers

- `find_latest_history_entry(...)`

Use this when you want one newest matching entry overall.

### Per-command latest helpers

- `latest_history_entries_by_command(...)`
- `find_latest_history_entries_by_command(...)`

Use these when you want the newest matching entry for each command separately.

### Per-command summary helpers

- `WorkflowHistoryCommandSummary`
- `summarize_history_entries_by_command(...)`
- `build_history_summary_by_command(...)`

Use these when you want compact rows with counts plus latest matching metadata per command.

### Audit snapshot helpers

- `WorkflowHistoryAuditSnapshot`
- `build_history_audit_snapshot(...)`
- `scan_history_audit_snapshot(...)`

Use these when you want one object containing:

- the filtered overall summary
- the newest matching entry per command
- the per-command summary rows
- the filter metadata used to build the snapshot

## CLI usage examples

The workflow CLI exposes a practical subset of this history surface directly.

```powershell
media-manager workflow history --path .\runs --command organize --record-type run_log --only-failed
media-manager workflow history --path .\runs --only-apply --has-reversible-entries --min-entry-count 10 --summary-only
media-manager workflow last --path .\runs --command trip --record-type execution_journal --only-successful
media-manager workflow history-latest-by-command --path .\runs --only-failed --summary-only
```

This keeps the audit logic in the core helpers while making the CLI useful for real triage and review work.

## Date-window audit use

You can narrow history inspection to a concrete ISO timestamp window.

Examples:

```powershell
media-manager workflow history --path .\runs --created-at-after 2026-04-01T00:00:00Z --created-at-before 2026-04-30T23:59:59Z
media-manager workflow last --path .\runs --command trip --created-at-after 2026-04-15T00:00:00Z
media-manager workflow history-latest-by-command --path .\runs --created-at-after 2026-04-01T00:00:00Z --only-successful
```

This is useful when you want to audit only one review cycle, one migration window, or one cleanup session without mixing in older runs.

## Practical reading path

If you need to work in this area, read in this order:

1. `docs/cli-workflows.md`
2. `src/media_manager/core/state/history.py`
3. `src/media_manager/cli_workflow.py`
4. matching tests in `tests/test_core_*history*` and `tests/test_cli_workflow_history*`
