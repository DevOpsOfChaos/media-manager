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

## Latest-per-command core helper

The history core now also supports a grouped view of **the newest matching entry per command**.

This is useful when you want a compact operational snapshot instead of a full chronological list.

Examples:

- newest matching `rename`, `organize`, `trip`, and `duplicates` runs in one result
- newest failed record for each command after a migration or cleanup session
- newest apply-requested entry per command inside one date window

The new helper names are:

- `latest_history_entries_by_command(...)`
- `find_latest_history_entries_by_command(...)`

These stay additive and do not change the behavior of the existing `history` or `last` calls.

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

## Latest-per-command overview

When you want a compact audit view instead of the full history list, the core helpers can now return the newest matching entry for each command.

That makes it easier to answer questions like:

- what is the latest `organize`, `rename`, `trip`, and `duplicates` run in this window?
- which commands most recently failed?
- what is the newest apply-oriented result per command?

This is designed to back an additive CLI overview without changing the existing `history` and `last` output contracts.
