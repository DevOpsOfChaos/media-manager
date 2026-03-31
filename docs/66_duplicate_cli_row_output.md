# Duplicate CLI row output

This step adds row-level visibility to `media-manager-duplicates`.

## New flags
- `--show-dry-run-rows`
- `--show-execution-rows`
- `--row-status planned|blocked|executable|deferred`

## Why this matters
Before this step, the duplicate CLI could already show:
- scan counters
- plan counters
- dry-run counters
- execution-preview counters
- audit and JSON artifacts

That was useful, but still too abstract when someone needed to answer a concrete question like:
- which rows are blocked?
- which delete rows are still executable?
- what exact reason is preventing execution?

## Current output model
Dry-run row output prints:
- row status
- action type
- reason
- source path
- survivor path
- target path

Execution-preview row output prints:
- row status
- row type
- reason
- source path
- survivor path
- target path

## Typical usage
```powershell
media-manager-duplicates --source "C:\Library" --policy first --mode delete --show-plan --show-dry-run-rows
```

Blocked execution rows only:

```powershell
media-manager-duplicates --source "C:\Library" --policy first --mode delete --show-execution-rows --row-status blocked
```

## Scope note
This is still a CLI visibility layer, not the final GUI duplicate execution surface.
But it closes a real usability gap immediately.
