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

## New filter directions

The core history helpers now support additive filtering for audit-focused workflows.

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

## Intended next CLI use

These helpers are designed so the workflow CLI can expose stronger history filtering without re-implementing audit logic in the command layer.

## CLI usage examples

The workflow CLI now exposes these filters directly.

```powershell
media-manager workflow history --path .\runs --command organize --record-type run_log --only-failed
media-manager workflow history --path .\runs --only-apply --has-reversible-entries --min-entry-count 10 --summary-only
media-manager workflow last --path .\runs --command trip --record-type execution_journal --only-successful
```

This keeps the audit logic in the core helpers while making the CLI useful for real triage and review work.

## Date-window audit use

You can now narrow history inspection to a concrete ISO timestamp window.

Examples:

```powershell
media-manager workflow history --path .\runs --created-at-after 2026-04-01T00:00:00Z --created-at-before 2026-04-30T23:59:59Z
media-manager workflow last --path .\runs --command trip --created-at-after 2026-04-15T00:00:00Z
```

This is useful when you want to audit only one review cycle, one migration window, or one cleanup session without mixing in older runs.

## Per-command summary layer

The core history helpers can now also collapse filtered history into one summary row per command.

Each per-command summary tracks:

- total matching entries for that command
- successful vs failed counts
- apply vs preview counts
- reversible totals
- record-type and exit-code summaries
- newest matching timestamp and path

This is useful when you want a compact operational view like:

- latest matching `rename`, `organize`, `trip`, and `duplicates` runs
- which commands failed most recently in a given date window
- which commands have apply-oriented history vs preview-only history
