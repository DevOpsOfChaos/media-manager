# Cleanup Workflow v2

`media-manager cleanup` now supports **controlled execution of one embedded step** while still keeping the workflow primarily review-oriented.

## What changed

The cleanup workflow can still build one combined report over:

- scan
- exact duplicates
- organize planning
- rename planning

In v2, it can also **apply one sub-step directly**:

- `--apply-organize`
- `--apply-rename`

This is intentionally narrower than a full one-shot destructive pipeline.

## Why the execution model stays narrow

The cleanup workflow is meant to guide the user through a messy multi-source situation.

Trying to auto-run duplicates, organize, and rename in one opaque command would make the system harder to trust and harder to undo.

So v2 allows only one focused apply step per run.

## Optional execution journal

When one apply step is selected, you can also write an undo-oriented execution journal:

```powershell
media-manager cleanup --source C:\Inbox --target C:\Library --apply-organize --journal logs\cleanup-organize.json
```

or

```powershell
media-manager cleanup --source C:\Inbox --target C:\Library --apply-rename --journal logs\cleanup-rename.json
```

## Current scope

- duplicates remain a review/planning stage
- organize apply can be triggered from the cleanup workflow
- rename apply can be triggered from the cleanup workflow
- execution journals are written only for the selected apply step

This gives the workflow a real execution path without collapsing everything into an unsafe black box.
