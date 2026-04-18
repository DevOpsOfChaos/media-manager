# Organize / Rename State + Duplicate Apply Parity Hardening v2

This block improves two practical areas:

1. command run logs and execution journals now contain better built-in summaries
2. `media-manager duplicates` gains run-log / journal parity with the other core CLI commands

## State / journaling improvements

`build_command_run_log()` now adds a lightweight `payload_summary` so large payloads remain easier to inspect at a glance.

`build_execution_journal()` now adds:

- `outcome_summary`
- `reason_summary`

That makes journals more useful without requiring downstream tooling to recompute basic counts every time.

## Duplicate CLI parity

`media-manager duplicates` now supports:

- `--run-log`
- `--journal` (with `--apply`)

This brings the duplicate workflow closer to organize / rename behavior.

## Organize / Rename / Inspect reporting

The CLI JSON payloads now expose clearer summary blocks directly:

- organize: status / reason / resolution / confidence summaries
- rename: dry-run and execution summaries
- inspect: source-kind, confidence, timezone, policy, and candidate parseability summaries

The goal is to keep the backend explainable and easier to integrate later.
