# Duplicate CLI workflow

This step turns `media-manager-duplicates` from a scan-only CLI into a real exact-duplicate workflow tool.

## Existing command
- `media-manager-duplicates`

## New capabilities
- auto-select keep candidates with `--policy first|newest|oldest`
- interpret decisions for `--mode copy|move|delete`
- save and restore exact-duplicate review decisions
- print cleanup-plan, dry-run, and execution-preview counters
- export a JSON report
- execute currently executable delete rows

## Main flags
- `--source <dir>` repeated for one or more source folders
- `--show-groups`
- `--policy first|newest|oldest`
- `--mode copy|move|delete`
- `--target <dir>`
- `--load-session <file>`
- `--save-session <file>`
- `--show-plan`
- `--json-report <file>`
- `--apply --yes`

## Current safety model
- `--apply` is only allowed together with `--mode delete`
- `--apply` requires `--yes`
- copy/move still stay in planning/preview territory
- delete execution only affects currently executable exact-duplicate delete rows

## Why this matters
The repo already had the exact-duplicate backend layers, but no strong operator-facing entry point that tied them together.
Now the duplicate feature is usable through:
- GUI review
- backend orchestration
- tests/CI
- and a workflow-aware CLI
