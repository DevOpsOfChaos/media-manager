# Media Manager

![Python](https://img.shields.io/badge/python-3.11%2B-blue)

Open-source media organization tool with CLI and modern desktop GUI. Organize, rename, find duplicates, detect people, and manage trip collections — all locally on your machine.

## Quick Start

```powershell
# Install
git clone https://github.com/YOUR_REPO/media-manager.git
cd media-manager
python -m pip install -e .

# CLI
media-manager duplicates --source C:\Photos --similar-images
media-manager organize --source C:\Inbox --target D:\Library --pattern "yyyy\\yyyy-MM-dd"

# Modern GUI
python -c "from src.media_manager.gui_desktop_qt_v2 import run; run()"
```

### Requirements
- Windows (primary), Python 3.11+
- **ExifTool** — download from https://exiftool.org (needed for organize/rename/trips)
- **PySide6** — `pip install pyside6` (needed for GUI)
- **dlib** (optional) — `pip install -e .[people]` (needed for face recognition)

## Features

| Feature | CLI | GUI |
|---------|-----|-----|
| Organize by date | `organize` | Yes |
| Rename with templates | `rename` | Yes |
| Exact duplicates | `duplicates` | Yes |
| Similar images | `--similar-images` | Yes |
| Face recognition | `people scan` | Setup page |
| Trip collections | `trip` | Yes |
| Safe preview | `--json` | Preview button |
| Undo | `undo --apply` | Planned |
| Media type filter | `--media-kind` | Dropdown |
| German / English | — | Flag toggle |

## GUI Pages

- **Dashboard** — Stats, quick actions, ExifTool status
- **Organize** — Sort files into date-pattern folders
- **Rename** — Rename with templates ({date}, {camera}, {index})
- **Duplicates** — Exact + similar scan with results table
- **People** — Face recognition setup + scan
- **Trips** — Create trip collections from date ranges
- **Settings** — Language (🇺🇸/🇩🇪), Theme (Dark/Light), default folders

The current focus is:

- inspect media metadata and date resolution
- plan and apply organize / rename operations
- review exact duplicates and similar-media candidates
- capture run history, journals, and undo-oriented artifacts
- compose repeatable workflows through presets, profiles, and bundles
- expose GUI-ready app metadata, run state, review workspaces, and guarded desktop entry points

## Product direction

Development priority is:

1. core foundation
2. CLI commands and safe preview/apply flows
3. state, journaling, history, and undo
4. duplicate and similar-media review
5. workflow helpers, reusable profiles, and profile bundles
6. app-service contracts and guarded GUI/workbench surfaces

## Core principles

- **Safety first** — preview before destructive actions
- **Idempotent behavior** — already compliant files should be skipped
- **Traceable decisions** — date choice, skip reasons, and target paths should stay explainable
- **Core/UI separation** — engine decisions belong in the core/application layer; the GUI must consume explicit contracts instead of duplicating behavior
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

`--run-dir` writes a timestamped run folder without changing the normal console output. Each run folder contains `command.json`, `report.json`, `review.json`, `summary.txt`, `ui_state.json`, `plan_snapshot.json`, and `action_model.json`; apply runs for commands that build journal entries also include `journal.json`. This is the recommended handoff format for repeatable CLI reviews and the gradually introduced GUI/workbench layer.

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

It is a serious core-first codebase with the CLI as the stable operational base and a controlled desktop GUI layer being introduced through tested contracts, safer execution, clearer reporting, and repeatable workflow operations.

## GUI-ready app metadata and run state

The CLI and app-service entry points expose a machine-readable app surface for the desktop GUI/workbench layer.
The goal is that the UI can discover supported workflows and render run results from JSON artifacts instead of parsing console text.

```powershell
media-manager app manifest
media-manager app manifest --json
media-manager-app manifest --json
media-manager app-services contracts
media-manager app-services contracts --json
media-manager app-services contract-bindings
media-manager app-services contract-bindings --json
media-manager app-services review-workbench
media-manager app-services review-workbench --json
media-manager app-services review-workbench --out-dir .\review-workbench-bundle
media-manager app-services review-workbench-interactions --json
media-manager app-services review-workbench-interactions --out-dir .\review-workbench-interactions
media-manager app-services review-workbench-callback-mounts --json
media-manager app-services review-workbench-callback-mounts --out-dir .\review-workbench-callback-mounts
media-manager app-services review-workbench-apply-preview --json
media-manager app-services review-workbench-apply-preview --out-dir .\review-workbench-apply-preview
media-manager app-services review-workbench-confirmation-dialog --json
media-manager app-services review-workbench-confirmation-dialog --out-dir .\review-workbench-confirmation-dialog
media-manager app-services review-workbench-apply-executor-contract --json
media-manager app-services review-workbench-apply-executor-contract --out-dir .\review-workbench-apply-executor-contract
media-manager app-services review-workbench-apply-handoff-panel --json
media-manager app-services review-workbench-apply-handoff-panel --out-dir .\review-workbench-apply-handoff-panel
media-manager app-services review-workbench-stateful-rebuild --intent-action set_query --intent-query people --json
media-manager app-services review-workbench-stateful-callbacks --callback-kind filter_query_changed --callback-query people --json
media-manager app-services review-workbench-stateful-rebuild --intent-action select_lane --intent-lane people-review --out-dir .\review-workbench-stateful-rebuild
media-manager app-services desktop-runtime --active-page review-workbench --json
```

The Review Workbench service is the first product-facing GUI bridge: it builds review lanes, a table model, controller state, a guarded Qt workbench payload, route intents, a Qt adapter descriptor package, a descriptor-only Qt widget binding plan, a lazy Qt widget skeleton, a local interaction plan, concrete callback mounts, a non-executing apply-preview command-plan contract, a guarded confirmation dialog model, and a disabled-by-default apply executor contract without importing PySide6, opening a window, or executing media operations. `desktop-runtime --active-page review-workbench` now treats Review Workbench as a real headless page, not a placeholder. The desktop Qt renderer consumes that skeleton through a PySide6-lazy builder. The interaction plan maps filter changes, lane selection, row activation, and toolbar actions to explicit non-executing UI intents; the callback mount plan wires those intents to concrete lazy Qt signal callbacks. The stateful callback bridge now connects those callbacks to the stateful rebuild loop, so filter/selection/reset/refresh callbacks can request a fresh `next_page_state` payload instead of mutating hidden GUI state. The apply-preview contract turns reviewed decisions into a confirmation-gated command-plan preview, and `review-workbench-confirmation-dialog` renders the risk summary, required checks, candidate commands, and typed confirmation phrase while still keeping command execution disabled. `review-workbench-apply-executor-contract` adds the disabled-by-default dry-run executor boundary: preflight checks, audit plan, mutation policy, and command previews exist, but execution remains off. `review-workbench-apply-handoff-panel` turns that boundary into a display-only GUI panel model with risk summary, typed-confirmation gate, preflight checklist, dry-run commands, audit rows, and disabled apply action. The stateful rebuild loop applies one local UI intent, reduces the current page state, and returns a replacement Review Workbench page-state bundle for the existing shell. It still does not import PySide6, open a window, write app state, execute commands, or perform media operations. Import smoke stays safe when the GUI extra is not installed.

The manifest includes command capabilities, supported options, risk levels, supported media formats, and the run-artifact contract. `media-manager app-services contracts --json` prints the GUI-facing app-service contract inventory: which headless payloads exist, what they consume, what they produce, which surfaces use them, and which safety boundary rules the GUI must follow. `media-manager app-services contract-bindings --json` validates the next layer: every app-service contract must bind to explicit GUI pages, panels, or shell surfaces before real Qt widgets consume it. The `review_workbench_service` contract is the main handoff point for the first real Review Workbench page; `review-workbench-widget-bindings` maps its adapter components to concrete Qt widget roles, models, signals, slots, and safe route dispatchers. `review-workbench-widget-skeleton` then converts that plan into the concrete mount tree consumed by `media_manager.gui_review_workbench_qt`. `review-workbench-interactions` maps the skeleton signals and toolbar actions to local state/reload/route intents. `review-workbench-callback-mounts` adds the concrete widget callback layer for filter widgets, the lane table, detail actions, and toolbar actions. `review-workbench-apply-preview` adds the reviewed command-plan preview, `review-workbench-confirmation-dialog` turns it into a guarded dialog model with checklist, risk summary, candidate commands, and typed confirmation requirements, and `review-workbench-apply-executor-contract` defines the disabled-by-default dry-run executor boundary while keeping actual media operations behind a later explicit execution path. `review-workbench-apply-handoff-panel` then exposes that boundary as a concrete GUI handoff panel without enabling execution. `review-workbench-stateful-rebuild` is the next UI loop: filter, selection, sort, paging, reset, and refresh intents rebuild the next Qt-consumable page state instead of mutating hidden GUI-only state. `review-workbench-stateful-callbacks` binds that loop to concrete lazy Qt callbacks and returns a safe callback response with `next_page_state` plus render-update metadata.

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

## App profiles for GUI presets

`media-manager app profiles` manages small JSON profile files that the GUI can use as saved presets. Profiles are intentionally structured data rather than raw shell snippets, so the GUI can show editable fields, validate risky choices, and render the final CLI command only when needed.

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
