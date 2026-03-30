# Execution safety wiring for associated files

This step wires the associated-file safety model into the real exact-duplicate execution path.

## What changed
The exact-duplicate workflow and execution runner now actively check for same-stem sibling files before allowing destructive delete execution.

## Wired modules
- `src/media_manager/execution_safety.py`
- `src/media_manager/duplicate_workflow.py`
- `src/media_manager/execution_runner.py`

## Effect
When a delete candidate has same-stem siblings in the same directory, for example:
- `IMG_0001.JPG`
- `IMG_0001.XMP`
- `IMG_0001.WAV`

then the duplicate execution path no longer treats the delete as safely executable.

### Workflow behavior
`build_duplicate_workflow_bundle(...)` now protects the execution preview before exposing it to later layers.

### Runner behavior
`run_duplicate_execution_preview(...)` performs the same associated-file guard again during execution.
This prevents unsafe deletion even if an older or unguarded preview somehow reaches the runner.

## Why duplicate protection exists twice
The guard is intentionally applied in two places:
- once during preview construction
- once again right before execution

That is deliberate defense in depth, not duplication by accident.
