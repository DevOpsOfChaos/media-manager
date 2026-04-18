# Duplicate Review / Audit v1

This block upgrades the existing exact-duplicate CLI from a basic scan-and-apply surface into a more reviewable workflow.

## New CLI capabilities

- `--show-dry-run-rows`
- `--show-execution-rows`
- `--row-status <planned|blocked|executable|deferred>`
- `--audit-log <path>`

## Why this matters

Exact duplicate handling becomes much safer when the user can inspect the rows that would actually be acted on.

This version focuses on:

- row-level visibility
- filtered review output
- structured audit artifacts for later inspection
- clearer exit code behavior for preview vs. apply runs

## Exit code policy

- `0` — scan succeeded and no execution errors occurred
- `1` — scan errors occurred
- `2` — execution errors occurred
- `3` — apply was requested but the run finished with blocked or deferred rows

## Audit log

The audit log is a JSON artifact intended for manual inspection, debugging, and later journaling work.

It includes:

- scan counters
- decision count
- cleanup-plan summary
- dry-run summary
- execution-preview summary
- execution-run row outcomes when an apply run occurred

## Scope

This is still not a full journaling/state layer.

It is a practical review-and-audit step that prepares the project for later workflow persistence.
