# State / History / Undo Diagnostics Hardening v2

This block strengthens the observability around workflow history and undo execution.

## What changed

- `WorkflowHistoryEntry` now exposes:
  - `successful`
  - `has_reversible_entries`
- New `build_history_summary(entries)` helper reports:
  - total / successful / failed entries
  - total reversible entries
  - record type summary
  - command summary
  - apply-requested summary
  - exit-code summary
  - latest timestamp

- `UndoExecutionResult` now exposes:
  - `ready_to_apply_count`
  - `status_summary`
  - `undo_action_summary`
  - `reason_summary`

- `media-manager workflow history --json` now includes a top-level `summary`.
- `media-manager workflow history` text output now shows a compact summary block.
- `media-manager workflow last --json` now includes additive `successful` and `has_reversible_entries`.
- `media-manager undo --json` now includes:
  - `ready_to_apply_count`
  - `status_summary`
  - `undo_action_summary`
  - `reason_summary`
- `media-manager undo` text output now shows these summaries as well.

## Why this is useful

These additions make run logs, journals, and undo previews easier to inspect without adding new fragile execution behavior.
The block is additive and intentionally avoids changing existing command semantics.
