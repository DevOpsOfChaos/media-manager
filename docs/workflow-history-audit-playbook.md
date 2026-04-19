# Workflow History Audit Playbook

This guide is a practical companion to the workflow history commands.

It is written for real review work, not just feature discovery.

## What the history layer is good for

Use the history layer when you want to answer questions like:

- What changed most recently?
- Which commands failed?
- Which runs were preview-only versus apply runs?
- Which runs produced reversible actions?
- What is the newest matching run per command?

## Start with the broad view

```powershell
media-manager workflow history --path .\runs
```

This gives you the overall picture:

- total matching entries
- successful versus failed runs
- reversible action counts
- apply versus preview counts
- command and record-type breakdowns

## Narrow by command

```powershell
media-manager workflow history --path .\runs --command organize
media-manager workflow history --path .\runs --command rename --json
```

Good for checking only one operational area without mixing in unrelated workflow runs.

## Narrow by record type

```powershell
media-manager workflow history --path .\runs --record-type run_log
media-manager workflow history --path .\runs --record-type execution_journal
```

A useful rule of thumb:

- `run_log` helps when you care about command-level reporting
- `execution_journal` helps when you care about reversible operations and undo-related review

## Focus on outcomes

```powershell
media-manager workflow history --path .\runs --only-successful
media-manager workflow history --path .\runs --only-failed
media-manager workflow history --path .\runs --only-apply
media-manager workflow history --path .\runs --only-preview
```

These are the filters you reach for when you want to triage what happened instead of just listing everything.

## Focus on meaningful runs

```powershell
media-manager workflow history --path .\runs --min-entry-count 10
media-manager workflow history --path .\runs --has-reversible-entries
media-manager workflow history --path .\runs --min-reversible-entry-count 3
```

This is especially useful when a directory contains many small smoke tests and only a few real runs.

## Focus on a time window

```powershell
media-manager workflow history --path .\runs --created-at-after 2026-04-01T00:00:00Z
media-manager workflow history --path .\runs --created-at-after 2026-04-01T00:00:00Z --created-at-before 2026-04-30T23:59:59Z
```

Good for:

- one migration window
- one review cycle
- one cleanup session
- one release validation pass

## Show only the newest matching entry

```powershell
media-manager workflow last --path .\runs
media-manager workflow last --path .\runs --command organize --only-successful
media-manager workflow last --path .\runs --record-type execution_journal --only-apply
```

Use `last` when you care about the single newest matching event.

## Show the newest matching entry per command

```powershell
media-manager workflow history-latest-by-command --path .\runs
media-manager workflow history-latest-by-command --path .\runs --only-failed
media-manager workflow history-latest-by-command --path .\runs --only-apply --summary-only
```

This is useful when you want a compact operational dashboard instead of one long list.

## JSON-focused review patterns

### Broad audit payload

```powershell
media-manager workflow history --path .\runs --json
```

Good when you want:

- machine-readable summaries
- post-processing
- snapshots in CI or scripted checks

### One newest event

```powershell
media-manager workflow last --path .\runs --command trip --json
```

Good when another tool needs just one current matching result.

### Latest entry per command

```powershell
media-manager workflow history-latest-by-command --path .\runs --json
```

Good when you want a compact per-command state snapshot.

## Suggested real-world audit flows

### 1. Review recent failures only

```powershell
media-manager workflow history --path .\runs --only-failed --created-at-after 2026-04-18T00:00:00Z
```

### 2. Check the latest successful apply run for organize

```powershell
media-manager workflow last --path .\runs --command organize --only-successful --only-apply
```

### 3. See the latest failure per command

```powershell
media-manager workflow history-latest-by-command --path .\runs --only-failed
```

### 4. Look only at meaningful execution journals

```powershell
media-manager workflow history --path .\runs --record-type execution_journal --has-reversible-entries --min-entry-count 5
```

## Good habits

- Use `history` for broad understanding
- Use `last` for one concrete newest event
- Use `history-latest-by-command` for compact dashboards
- Add date filters early when you know the relevant review window
- Add `--summary-only` when you want a stable human-readable snapshot without long entry lists
- Prefer JSON output when the result will be consumed by scripts or saved as evidence

## Pairing with profiles and bundles

History review becomes more useful when you also keep profile and bundle operations disciplined.

A solid operating loop is:

1. preview with profiles or bundles
2. run apply deliberately
3. inspect history
4. inspect the latest event or latest-per-command state
5. only then continue with further changes

That workflow keeps the CLI useful as a trustworthy operational product instead of just a command launcher.
