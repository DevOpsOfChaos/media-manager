# Workflow History Triage Scenarios

This guide focuses on practical history triage once a run directory already contains a mix of run logs and execution journals.

It is written for the current CLI-first product line where history inspection, undo-related artifacts, and workflow review are part of daily usage rather than occasional debugging.

## What to check first

Before drilling into one command, establish four basics:

1. Is the directory actually populated with recognized history files?
2. Are you looking for one command, one time window, or one apply/preview mode?
3. Do you care about all entries, only the latest one, or the latest per command?
4. Do you need raw entry details or just a compact audit summary?

## Fast triage patterns

### 1. Broad snapshot of a run folder

```powershell
media-manager workflow history --path .\runs
```

Use this first when you want overall counts:

- total matching entries
- success vs. failure
- apply vs. preview
- exit-code spread
- latest recognized timestamp

### 2. Only failed work

```powershell
media-manager workflow history --path .\runs --only-failed
```

Use this when the folder contains many successful runs and you only care about repair work.

### 3. One command in one review window

```powershell
media-manager workflow history --path .\runs --command organize --created-at-after 2026-04-01T00:00:00Z --created-at-before 2026-04-30T23:59:59Z
```

This is the best pattern when you want to isolate one migration, one cleanup batch, or one rollout window.

### 4. Latest matching run only

```powershell
media-manager workflow last --path .\runs --command trip --only-successful
```

Use this when you need the newest single matching entry, not a whole review list.

### 5. Latest matching run per command

```powershell
media-manager workflow history-latest-by-command --path .\runs --only-failed
```

This is useful when several commands are active in the same run directory and you want the newest failure for each command instead of a long mixed history.

## Practical investigation recipes

### Find preview runs that should probably have become apply runs

```powershell
media-manager workflow history --path .\runs --only-preview --only-successful --summary-only
```

Interpretation:

- many successful previews can mean the operator is reviewing correctly
- but they can also reveal that successful review sessions are never being promoted into real apply runs

### Find risky apply sessions with real reversible work

```powershell
media-manager workflow history --path .\runs --only-apply --has-reversible-entries --summary-only
```

Interpretation:

- these are the runs that most deserve extra scrutiny and artifact retention
- they are also the most likely candidates for follow-up undo validation

### Separate run logs from execution journals

```powershell
media-manager workflow history --path .\runs --record-type run_log
media-manager workflow history --path .\runs --record-type execution_journal
```

Interpretation:

- run logs help with command-level accountability
- execution journals help with action-level reversibility and deeper operational review

### Focus on larger runs only

```powershell
media-manager workflow history --path .\runs --min-entry-count 25
```

Interpretation:

- this removes smoke tests and tiny experiments
- it gives a better view of production-sized sessions

## Choosing the right command

Use `workflow history` when you need:

- all matching entries
- totals and summaries
- a timeline feel

Use `workflow last` when you need:

- one newest matching entry
- a direct answer for a specific question

Use `workflow history-latest-by-command` when you need:

- one newest matching entry per command
- quick coverage across rename / organize / duplicates / trip / cleanup without reading a long stream

## JSON-first review flows

For machine-friendly or notebook-friendly review, prefer:

```powershell
media-manager workflow history --path .\runs --json
media-manager workflow last --path .\runs --command organize --json
media-manager workflow history-latest-by-command --path .\runs --json
```

Keep in mind:

- older JSON contracts should be extended additively, not reshaped
- top-level fields that existing tests expect should remain stable
- if a new field is needed, add it rather than moving an existing one

## Recommended operator habit

When a change touches history behavior, check in this order:

1. direct new test file for the feature
2. older history compatibility tests
3. full `pytest -q`

This catches the most common failure mode in this area: a feature that looks correct in isolation but silently breaks older JSON, import, or summary expectations.
