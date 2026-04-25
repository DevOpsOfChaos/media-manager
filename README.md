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
media-manager duplicates --source C:\Photos --source D:\Phone --json
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

The doctor command validates paths, export destinations, include/exclude filters, and common workflow inputs without moving, copying, renaming, or deleting files. The direct `media-manager-doctor` script is available after reinstalling the package, for example with `python -m pip install -e .`; `media-manager doctor` works through the main CLI entry point.

## Structured run artifacts

```powershell
media-manager organize --source C:\Inbox --target D:\Library --run-dir .\runs
media-manager rename --source C:\Inbox --run-dir .\runs
media-manager duplicates --source C:\Photos --media-kind video --run-dir .\runs
media-manager cleanup --source C:\Photos --target E:\Library --run-dir .\runs
```

`--run-dir` writes a timestamped run folder without changing the normal console output. Each run folder contains `command.json`, `report.json`, `review.json`, `summary.txt`, `ui_state.json`, `plan_snapshot.json`, and `action_model.json`; apply runs for commands that build journal entries also include `journal.json`. This is the recommended handoff format for repeatable CLI reviews and later GUI integration.

Inspect existing run folders with:

```powershell
media-manager runs --run-dir .\runs list
media-manager runs --run-dir .\runs show 20260425T113557Z-organize-preview
media-manager runs --run-dir .\runs validate
```

The direct `media-manager-runs` script is available after reinstalling the package; `media-manager runs` works through the main CLI entry point.

## Duplicate review and reports

```powershell
media-manager duplicates --source C:\Photos --source D:\Phone --json
media-manager duplicates --source C:\Photos --source D:\Videos --media-kind video --json
media-manager duplicates --source C:\Music --media-kind audio --json
media-manager duplicates --source C:\Photos --include-extension .mp4 --include-extension .mov --show-groups
media-manager duplicates --list-supported-formats
media-manager duplicates --source C:\Photos --policy first --mode delete --report-json .\reports\duplicates.json --review-json .\reports\duplicates-review.json
media-manager duplicates --source C:\Photos --export-decisions .\reports\duplicate-decisions.json
media-manager duplicates --source C:\Photos --import-decisions .\reports\duplicate-decisions.json --mode delete --show-plan
media-manager duplicates --source C:\Photos --include-pattern "*.jpg" --exclude-pattern "*edited*" --show-plan
```

Exact duplicate scanning is byte-based and now covers a broad photo, RAW, video, and audio catalog. Use `--media-kind video`, `--media-kind audio`, repeated `--include-extension`, or repeated `--exclude-extension` to narrow large scans before hashing. For review-first workflows, write an editable duplicate decision file with `--export-decisions`, set `selected_keep_path` for each group, then load it with `--import-decisions`. Duplicate delete remains review-first: `--apply` only works with `--mode delete --yes`, and associated sibling files still block executable delete rows for manual review.

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

## GUI-ready app metadata and run state

The CLI now exposes a small machine-readable app surface for a future desktop GUI.
The goal is that a UI can discover supported workflows and render run results from JSON artifacts instead of parsing console text.

```powershell
media-manager app manifest
media-manager app manifest --json
media-manager-app manifest --json
```

The manifest includes command capabilities, supported options, risk levels, supported media formats, and the run-artifact contract.

Run artifact folders created with `--run-dir` also include GUI-facing artifacts:

```text
ui_state.json
plan_snapshot.json
action_model.json
```

`ui_state.json` is a compact dashboard object with an overview, review preview, section cards, and suggested actions. `plan_snapshot.json` is a compact table/list snapshot for plan previews and review screens. `action_model.json` describes enabled, recommended, blocked, and confirmation-required actions so a GUI can render safe buttons without deriving behavior from free text. These files are generated alongside `command.json`, `report.json`, `review.json`, and `summary.txt`.

You can also build UI state from an existing report:

```powershell
media-manager app ui-state --command duplicates --report-json .\runs\<run-id>\report.json --command-json .\runs\<run-id>\command.json --run-id <run-id> --out .\runs\<run-id>\ui_state.json
media-manager app plan-snapshot --command duplicates --report-json .\runs\<run-id>\report.json --run-id <run-id> --out .\runs\<run-id>\plan_snapshot.json
media-manager app action-model --command duplicates --report-json .\runs\<run-id>\report.json --command-json .\runs\<run-id>\command.json --run-id <run-id> --out .\runs\<run-id>\action_model.json
```

The run browser can show both directly:

```powershell
media-manager runs --run-dir .\runs show <run-id> --artifact ui-state
media-manager runs --run-dir .\runs show <run-id> --artifact plan-snapshot
media-manager runs --run-dir .\runs show <run-id> --artifact action-model
```

## App profiles for future GUI presets

`media-manager app profiles` manages small JSON profile files that a future GUI can use as saved presets. Profiles are intentionally structured data rather than raw shell snippets, so the GUI can show editable fields, validate risky choices, and render the final CLI command only when needed.

Create a profile:

```powershell
media-manager app profiles init --out .\profiles\video-duplicates.json --command duplicates --title "Video duplicate review" --source D:\Media --media-kind video --run-dir .\runs --favorite
```

List profiles:

```powershell
media-manager app profiles list --profile-dir .\profiles
media-manager app profiles list --profile-dir .\profiles --json
```

Inspect, validate, or render a profile:

```powershell
media-manager app profiles show .\profiles\video-duplicates.json
media-manager app profiles validate .\profiles\video-duplicates.json --json
media-manager app profiles render .\profiles\video-duplicates.json
```

A profile render is non-executing. It only prints the command preview, which keeps saved GUI presets separate from actual file operations.
