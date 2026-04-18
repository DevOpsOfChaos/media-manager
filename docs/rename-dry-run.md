# Rename Dry-Run v1

## Goal

Provide a safe, explainable rename planning step on top of the new scanner and date-resolver foundation.

The current version is intentionally **dry-run only**.

## What it does

- scans one or more source folders
- resolves a capture datetime for each media file
- renders a proposed new file name from a template
- reports whether each file is planned, skipped, conflicting, or errored

## Supported template tokens

- `{date:%Y-%m-%d_%H-%M-%S}`
- `{datetime:%Y-%m-%d_%H-%M-%S}`
- `{year}`
- `{month}`
- `{day}`
- `{hour}`
- `{minute}`
- `{second}`
- `{year_month}`
- `{year_month_day}`
- `{stem}`
- `{suffix}`
- `{source_name}`
- `{index}`

## Example

```powershell
media-manager rename --source C:\Photos --template "{date:%Y-%m-%d_%H-%M-%S}_{stem}" --show-files
```

## Current safety rules

- no apply mode yet
- files already matching the rendered target name are skipped
- existing target names are conflicts
- multiple source files resolving to the same target name are conflicts

## Why dry-run first

Rename behavior must be predictable before it becomes destructive.

This step gives the project a stable rename-planning layer that can later gain:

- apply mode
- idempotence memory
- presets
- conflict resolution strategies
