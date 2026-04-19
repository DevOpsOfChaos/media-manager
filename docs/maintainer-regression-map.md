# Maintainer Regression Map

This document is a practical checklist for choosing the right regression scope before handing off a ZIP update.

It focuses on the patterns that have repeatedly caused avoidable breakage:

- package export mismatches
- `core.state.__init__` re-export drift
- dataclass/output-shape compatibility
- Windows path handling
- new tests that only validate the happy path but miss broad regressions

## When only a few history helpers changed

At minimum run:

```powershell
pytest -q tests/test_core_history_audit_snapshot_v1.py
pytest -q tests/test_core_history_latest_by_command_v1.py
pytest -q tests/test_core_history_summary_by_command_v1.py
pytest -q tests/test_core_state_history_hardening_v2.py
```

Then run:

```powershell
pytest -q
```

Reason:

History helper changes can still break:

- `core.state.__init__` exports
- workflow CLI imports
- shell/workflow modules that import state helpers indirectly

## When `core.state.__init__.py` changed

Treat this as broad-risk even if the file is small.

At minimum verify imports used by:

- cleanup CLI
- organize CLI
- rename CLI
- trip CLI
- duplicates CLI
- workflow CLI
- undo CLI
- workflow core modules that import state helpers directly

Recommended command:

```powershell
pytest -q
```

Reason:

A single missing re-export in `core.state.__init__` can cause dozens of collection-time import failures.

## When workflow history JSON changed

Run focused tests for:

- `tests/test_cli_workflow_history_v2.py`
- `tests/test_cli_workflow_history_filters_v1.py`
- `tests/test_cli_workflow_last_json_compat_v1.py`

Then run:

```powershell
pytest -q
```

Reason:

The workflow history JSON surface has multiple compatibility-sensitive shapes:

- collection payloads
- single-entry payloads
- nested `entry` payloads plus top-level compatibility fields
- root path versus entry path fields

## When bundle/profile selection changed

Run at minimum:

- `tests/test_workflow_profile_selection_filters.py`
- `tests/test_core_workflow_profile_bundle_v1.py`
- relevant CLI workflow tests

Also watch for:

- slash versus backslash handling
- relative bundle paths versus filesystem paths
- missing exports in `core.workflows.__init__`

## When dataclasses changed

Before handoff, check:

- positional constructor compatibility
- default ordering of new fields
- older tests that instantiate dataclasses directly

Reason:

Adding new fields in the wrong position can silently break older tests even if all new tests pass.

## When adding new CLI commands

Prefer this pattern:

1. add a new command
2. add a new test file dedicated to that command
3. keep existing commands unchanged
4. only after that consider reuse/refactor

Reason:

A new command has much lower regression risk than reshaping an existing compatibility-sensitive one.

## Windows-specific checks

Whenever paths are filtered, serialized, or written into portable JSON/bundle payloads, check:

- slash and backslash input variants
- whether a path should stay a `Path` object internally
- whether a serialized field must be a `str`
- whether portable bundle paths should be forced to `/`

## Final handoff rule

If the change touches:

- `__init__.py`
- CLI JSON output
- workflow bundle/profile dataclasses
- state/history helper exports

then a focused subset is **not enough**.

Run the focused subset first, but do not hand off as green before a full:

```powershell
pytest -q
```

## Practical bias

When in doubt:

- prefer additive new files
- prefer additive new commands
- prefer new docs over risky reshapes when the repo is already in a delicate state
- prefer one cumulative replacement file over multiple overlapping mini-fixes
