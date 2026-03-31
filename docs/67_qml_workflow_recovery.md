# QML workflow recovery baseline

This note captures the current trustworthy baseline for the QML workflow work.

## Why this document exists

Recent `Main.qml` rewrite attempts produced structurally broken QML states on stacked PR branches.
That made the branch history noisy and created confusion about which branch is still a valid base for further UI work.

This document freezes the current truth so the next UI step can be narrow and deliberate instead of speculative.

## Trustworthy branch baseline

Current trustworthy UI/backend baseline for QML workflow work:
- branch: `assistant/duplicate-audit-log`
- PR: `#4`

This branch already contains:
- the stronger duplicate backend and CLI foundation
- the current `qml_app.py` property and slot contract
- a readable `Main.qml` that is at least structurally plausible for further editing

## Branches that should not be treated as truth

The following stacked experimental branches are not a safe base for future work:
- `assistant/qml-valid-main-window-shell`
- `assistant/qml-structurally-valid-workflow-shell`

Reason:
- they introduced text corruption and syntax corruption into `Main.qml`
- they are useful only as failed experiments, not as a continuation base

## Current backend contract that already exists

The current `qml_app.py` already exposes the duplicate planning data needed for stronger summary-stage visibility.

Already available properties include:
- `summaryReadyForDryRun`
- `summaryDecisionStatus`
- `summaryExactGroupCount`
- `summaryExactDuplicateFiles`
- `summaryExtraDuplicates`
- `summaryOperationModeLabel`
- `dryRunReady`
- `dryRunStatusLabel`
- `dryRunRowsCountLabel`
- `dryRunFilterKey`
- `dryRunFilterOptions`
- `dryRunRows`
- `executionReady`
- `executionStatusLabel`
- `executionRowsCountLabel`
- `executionRows`
- `sortingPreviewRows`
- `renamePreviewRows`

Already available slots and actions include:
- `setDryRunFilter(...)`
- `workflowNext()`
- `workflowBack()`
- duplicate keep-selection actions
- sorting builder actions
- rename builder actions

## What the next real UI step should be

The next useful step is not another broad `Main.qml` rewrite.

The next useful step is:
- start from `assistant/duplicate-audit-log`
- keep the existing stable page structure
- modify only the workflow summary area
- surface:
  - dry-run status
  - dry-run row filters
  - dry-run rows
  - execution-preview status
  - execution-preview rows

## Scope guard

The next implementation pass should **not**:
- redesign the whole window
- replace the sidebar/navigation structure
- invent new backend properties if existing ones already cover the UI need
- continue from the broken PR-7/8 rewrite stack

The next implementation pass **should**:
- stay on the trustworthy PR-4 baseline
- make one narrow summary-stage visibility change
- verify against the existing `qml_app.py` contract
- keep README/roadmap truth aligned after the UI work lands

## Practical consequence

The repo does not currently need more duplicate backend foundation.
The repo needs a careful QML recovery from the last broken rewrite attempt and then a narrow duplicate summary UI enhancement.
