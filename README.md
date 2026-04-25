# Media Manager

![Python](https://img.shields.io/badge/python-3.11%2B-blue)

Open-source CLI-first media organization software for photos and videos.

## What this repository is

This repository is the active product baseline for **core-first media management on Windows**.

The current focus is:

- inspect media metadata and date resolution
- plan and apply organize / rename operations
- review exact duplicates and similar-media candidates
- capture run history, journals, and undo-oriented artifacts
- compose repeatable workflows through presets, profiles, and bundles

## Product direction

Development priority is:

1. core foundation
2. CLI commands and safe preview/apply flows
3. state, journaling, history, and undo
4. duplicate and similar-media review
5. workflow helpers, reusable profiles, and profile bundles
6. GUI later

## Core principles

- **Safety first** — preview before destructive actions
- **Idempotent behavior** — already compliant files should be skipped
- **Traceable decisions** — date choice, skip reasons, and target paths should stay explainable
- **Core/UI separation** — engine decisions belong in the core, not in a future GUI
- **Windows first** — Windows is the primary target for current examples and workflows
- **English first** — CLI output and JSON contracts stay English for now

## Common commands

```powershell
media-manager inspect C:\Photos\IMG_0001.jpg
media-manager organize --source C:\Inbox --target D:\Library --pattern yyyy\\yyyy-MM-dd
media-manager rename --source C:\Inbox --template "{date}_{original_name}"
media-manager duplicates C:\Photos D:\Phone --json
media-manager doctor --command cleanup --source C:\Photos --source D:\Phone --target E:\Library
media-manager cleanup --source C:\Photos --source D:\Phone --target E:\Library --apply
media-manager trip --source C:\Photos --target E:\Trips --label Italy --start 2025-06-01 --end 2025-06-14
media-manager undo --path .\runs\2026-04-18-execution-journal.json --apply
```

## Diagnostics

```powershell
media-manager doctor --command organize --source C:\Inbox --target D:\Library
media-manager doctor --command cleanup --source C:\Photos --target E:\Library --include-pattern "*.jpg" --exclude-pattern "*edited*"
media-manager doctor --source C:\Inbox --report-json .\reports\doctor.json
```

The doctor command validates paths, export destinations, include/exclude filters, and common workflow inputs without moving, copying, renaming, or deleting files.

## Workflow layer

```powershell
media-manager workflow presets
media-manager workflow render-preset cleanup-family-library --source C:\Photos --source D:\Phone --target E:\Library
media-manager workflow profile-save .\profiles\family-cleanup.json --preset cleanup-family-library --source C:\Photos --source D:\Phone --target E:\Library
media-manager workflow profile-list --profiles-dir .\profiles
media-manager workflow profile-run-dir --profiles-dir .\profiles --only-valid
media-manager workflow profile-bundle-write .\bundles\profiles.json --profiles-dir .\profiles
media-manager workflow profile-bundle-run .\bundles\profiles.json --only-valid
media-manager workflow profile-bundle-sync .\bundles\profiles.json --target-dir .\profiles-restored --apply
```

## Workflow history

```powershell
media-manager workflow history --path .\runs
media-manager workflow history --path .\runs --command organize --only-failed --record-type run_log
media-manager workflow history-latest-by-command --path .\runs --summary-only
media-manager workflow history-summary-by-command --path .\runs --summary-only
media-manager workflow last --path .\runs --command cleanup --only-successful
```

## Requirements

- Windows is the primary target right now
- Python 3.11+
- ExifTool

## Development

Run tests:

```powershell
pytest -q
```

## Scope statement

This is not yet a finished consumer-facing media manager.

It is a serious CLI/core-first codebase aimed at becoming a trustworthy media-management product with safer execution, clearer reporting, and repeatable workflow operations.
