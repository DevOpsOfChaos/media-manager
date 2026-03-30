# Duplicate execution runner

This step adds a narrow execution runner for the exact-duplicate execution preview.

## Added module
- `src/media_manager/execution_runner.py`

## Current scope
The runner intentionally executes only the already-modeled exact-duplicate execution preview.

### Supported behavior
- `filesystem_delete` + `executable` can be previewed or actually deleted
- `pipeline_exclusion` stays deferred until later copy/move pipeline integration exists
- `blocked` stays blocked

## Entry point
- `run_duplicate_execution_preview(preview, apply=False)`

## Safety model
- Default is preview-only (`apply=False`)
- Missing source files are reported as execution errors
- Move/copy duplicate exclusions are not executed yet because the wider pipeline is not wired

## Why this matters
Before this step, the project had:
- exact-duplicate scan
- cleanup dry-run model
- execution preview model

But it still lacked a narrow runner that could turn the delete-path preview into a real action layer.

This runner is the first step toward a later user-facing execution stage.
