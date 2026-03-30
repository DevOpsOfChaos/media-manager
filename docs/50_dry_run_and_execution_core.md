# Dry-Run and Execution Core

## Purpose

The product already lets the user:
- scan exact duplicates
- choose a keep candidate
- preview sorting
- preview rename

But it still has a major credibility gap:
it can describe decisions without turning them into an explicit operation plan.

This file defines the next core layer:
a real dry-run model for exact duplicate cleanup.

## What this adds

The cleanup core now provides:
- `ExactCleanupDryRun`
- `DryRunAction`
- `build_exact_cleanup_dry_run(...)`

This turns exact duplicate decisions into explicit rows with:
- action type
- operation mode
- source path
- survivor path
- optional target path
- size
- reason
- status

## Why this matters

Without a dry-run model, the UI can only show summary text and counts.
With a dry-run model, the UI can later show:
- a real operations table
- filters by action type
- blocked rows
- reasons for destructive or excluded actions
- the bridge into real execution

## Current interpretation rules

For exact duplicates only:

- `delete` mode -> duplicate candidates become `delete`
- `move` mode -> duplicate candidates become `exclude_from_move`
- `copy` mode -> duplicate candidates become `exclude_from_copy`

This is intentionally conservative.
At this stage the software still does not execute anything.
It only describes what the current decisions imply.

## Blocked rows

If an exact group has no keep decision yet, the dry run emits blocked rows:
- `action_type = blocked_exact_group`
- `status = blocked`
- `reason = missing_keep_decision`

This makes uncertainty explicit instead of hiding it.

## What should happen next

The next visible product step should be:
- expose the new dry-run rows in `qml_app.py`
- insert a dedicated dry-run stage between summary and sorting
- show planned rows and blocked rows in a real table
- only after that, start building actual execution

## Deliberately out of scope

This core still does not handle:
- similarity decisions
- associated-file coupling
- sorting execution
- rename execution
- collision resolution
- filesystem writes

Those come later.
