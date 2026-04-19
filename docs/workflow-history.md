# Workflow history

The workflow history layer is meant to support review, auditing, and repeatable reruns.

## What counts as workflow history

The current history helpers recognize two main record shapes:

- command run logs
- execution journals

Both are normalized into `WorkflowHistoryEntry` records so they can be filtered and summarized together.

## Core filtering

The core helpers now support more than simple command filtering.

Useful filters include:

- `command_name`
- `record_type`
- `only_successful`
- `only_failed`
- `only_apply_requested`
- `only_preview`
- `has_reversible_entries`
- `min_entry_count`
- `min_reversible_entry_count`
- `created_at_after`
- `created_at_before`

That makes it easier to answer questions like:

- What was the latest successful trip apply run this week?
- Which execution journals in a date window still contain reversible entries?
- Which runs in the last few days actually touched many planned items?

## Timestamp window behavior

`created_at_after` and `created_at_before` expect ISO-like timestamps.

Examples:

- `2026-04-10T00:00:00+00:00`
- `2026-04-10T12:30:00Z`

When a date-window filter is active, entries with invalid or missing timestamps are excluded from that filtered result.

## Current scope

This block hardens the core helpers first.

That means the filter logic is available for:

- direct Python usage
- internal higher-level CLI wiring
- future reporting and audit commands

The goal is to keep history inspection additive and review-oriented rather than bolting on fragile output-only behavior.
