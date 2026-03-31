# Duplicate execution audit log

This step adds a dedicated audit-log path for exact-duplicate execution runs.

## Added module
- `src/media_manager/execution_audit.py`

## CLI integration
- `media-manager-duplicates --audit-log <file>`

## Purpose
The duplicate feature already had:
- scan
- review decisions
- dry-run model
- execution preview
- execution runner
- JSON report

But real or preview execution still lacked a focused audit artifact that could be kept as a run record.

## What the audit log captures
- UTC creation timestamp
- whether apply was requested
- scan counters
- decision count
- cleanup-plan counters
- dry-run counters
- execution-preview counters
- execution-run counters and per-entry outcomes when available

## Why this matters
A general report is useful, but an execution audit log is the better artifact when someone later asks:
- what did this run actually try to do?
- what was previewed versus applied?
- which files were blocked, deferred, trashed, or failed?

That makes the execution path more defensible and easier to inspect after the fact.
