
# Cleanup workflow v1

`media-manager cleanup` is a guided dry-run workflow for a common real-world problem:

- multiple unsorted source folders
- possible exact duplicates
- a future organize target
- a future rename template

## Current scope

This workflow is intentionally **dry-run only** in v1.

It combines these subsystems into one report:

1. exact duplicate scan
2. optional duplicate keep decisions
3. organize dry-run plan
4. rename dry-run plan

## Example

```powershell
media-manager cleanup `
  --source C:\Phone `
  --source D:\OldBackups `
  --target E:\Library `
  --duplicate-policy first `
  --organize-pattern "{year}/{year_month_day}" `
  --rename-template "{date:%Y-%m-%d_%H-%M-%S}_{stem}" `
  --json
```

## Why this is useful

This command does not mutate files yet, but it gives a single entry point for:

- understanding how many duplicates exist
- seeing whether duplicate decisions can already be resolved
- previewing destination organization
- previewing rename decisions

## Run log support

You can also write a JSON run log:

```powershell
media-manager cleanup ... --run-log logs\cleanup.json
```

That log can later become the basis for richer workflow history and journaling.
