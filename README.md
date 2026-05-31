# Media Manager

![Python](https://img.shields.io/badge/python-3.11%2B-blue)

Open-source media organization tool with CLI and a Tauri + React + TypeScript desktop frontend. Organize, rename, find duplicates, detect people, and manage trip collections — all locally on your machine.

## Features

- **Magic bytes detection** — identify file types by content signature, ignoring extensions
- **Deep metadata extraction** — EXIF, IPTC, XMP, MakerNotes with completeness scoring
- **Auto-tagging** — generate semantic tags (camera, date, GPS, ISO, season, focal range)
- **File health checker** — detect corrupted/truncated JPEGs, PNGs by structural validation
- **Smart album suggestions** — date-cluster and camera-based album groupings
- **Organize by date** — automatically sort media into date-based folder structures
- **Rename with templates** — batch rename using EXIF date, camera model, and custom patterns
- **Exact duplicates** — byte-level detection across photos, RAW, video, and audio
- **Similar images** — perceptual hashing for near-duplicate detection
- **Face recognition** — detect, name, merge, and search people in your library
- **Trip collections** — filter and group media by date range with labels
- **Safe preview** — all destructive operations preview before execution
- **Undo** — revert operations via execution journals
- **Hardlink support** — organize without duplicating data (`--operation-mode hardlink`)
- **Job queue** — pause/resume long-running operations with status tracking
- **Watch mode** — monitor directories for automatic processing
- **Stats dashboard** — overview of media library size, types, and dates
- **Custom tags + color labels + star ratings** — catalog metadata stored in sidecar files
- **Contact sheets** — generate PDF contact sheets from image lists
- **Web gallery** — export static HTML photo galleries
- **Desktop UI** — Tauri + React + TypeScript frontend with shadcn/ui
- **German / English** — bilingual CLI and UI (`--language`)

## Installation

### Prerequisites
- **Windows** (primary target), Python 3.11+
- **ExifTool** — download from https://exiftool.org (required for organize/rename/trips)
- **dlib** (optional) — `pip install -e .[people]` (required for face recognition)
- **Node.js 18+** and **Rust** — for desktop UI development

### CLI install
```powershell
git clone https://github.com/DevOpsOfChaos/media-manager.git
cd media-manager
python -m pip install -e .
```

### Desktop UI install
```powershell
cd desktop
npm install
npm run tauri dev
```

### Verify installation
```powershell
media-manager doctor --help
media-manager app manifest
```

## CLI Commands

### Organize
```powershell
media-manager organize --source C:\Inbox --target D:\Library --pattern "yyyy\\yyyy-MM-dd"
media-manager organize --source C:\Inbox --target D:\Library --operation-mode hardlink
```
Preview by default. Add `--apply` to execute.

### Rename
```powershell
media-manager rename --source C:\Inbox --template "{date}_{original_name}"
media-manager rename --source C:\Inbox --template "{camera}_{date:%Y-%m-%d}_{stem}"
```

### Duplicates
```powershell
media-manager duplicates --source C:\Photos --source D:\Phone --json
media-manager duplicates --source C:\Photos --include-extension .mp4 --show-groups
media-manager duplicates --source C:\Photos --policy first --mode delete --yes --apply
media-manager duplicates --source C:\Photos --similar-images
media-manager duplicates --list-supported-formats
```

### Face Recognition
```powershell
media-manager people scan --source C:\Photos
media-manager people catalog-list --catalog-path .\catalog.json
media-manager people person-rename --person-id abc123 --name "Jane"
media-manager people person-merge --from abc123 --to def456
```

### Trip Collections
```powershell
media-manager trip --source C:\Photos --target E:\Trips --label Italy --start 2025-06-01 --end 2025-06-14
```

### File Operations
```powershell
media-manager file exif C:\Photos\IMG_0001.jpg
media-manager file export --source C:\img.jpg --target C:\out.jpg --width 2048
media-manager file integrity --paths paths.json
media-manager file contact-sheet --paths img.json --output sheet.pdf --cols 4
media-manager file web-gallery --paths img.json --output-dir .\gallery --title "Photos"
media-manager file backup
```

### Doctor (Preflight Checks)
```powershell
media-manager doctor --command organize --source C:\Inbox --target D:\Library
media-manager doctor --command cleanup --source C:\Photos --target E:\Library
media-manager doctor --source C:\Inbox --report-json .\reports\doctor.json
```

### Run History & Artifacts
```powershell
media-manager organize --source C:\Inbox --target D:\Library --run-dir .\runs
media-manager runs --run-dir .\runs list
media-manager runs --run-dir .\runs show 20260425T113557Z-organize-preview
media-manager runs --run-dir .\runs validate
```

### Workflows
```powershell
media-manager workflow presets
media-manager workflow profile-save .\profiles\cleanup.json --preset cleanup-family-library --source C:\Photos --target E:\Library
media-manager workflow profile-bundle-run .\bundles\profiles.json
```

### Undo
```powershell
media-manager undo --path .\runs\2026-04-18-execution-journal.json --apply
```

### Watch Mode
```powershell
media-manager watch --source C:\Inbox --target D:\Library --pattern "yyyy\\yyyy-MM-dd"
```

### Stats
```powershell
media-manager stats --source C:\Photos --source D:\Phone
```

### App Services (GUI Contracts)
```powershell
media-manager app manifest --json
media-manager app-services contracts --json
media-manager app-services review-workbench --json
media-manager app profiles list --profile-dir .\profiles --json
```

## Development

### Setup
```powershell
git clone https://github.com/DevOpsOfChaos/media-manager.git
cd media-manager
python -m pip install -e .[dev]
cd desktop
npm install
```

### Project Structure
```
media-manager/
  src/media_manager/       # Python core (CLI, bridges, core logic)
  desktop/                 # Tauri + React + TypeScript desktop frontend
    src/lib/               # Tauri bridge API layer
    src/pages/             # UI pages (Library, Organize, Duplicates, People, etc.)
    src/components/        # Reusable UI components (shadcn/ui based)
    src-tauri/             # Rust backend (Tauri)
  tests/                   # Python test suite
  docs/                    # Documentation
```

### Run Tests
```powershell
# Python tests
pytest -q

# TypeScript type check
cd desktop && npx tsc --noEmit
```

### Run Desktop UI
```powershell
cd desktop
npm run tauri dev
```

### Linting
```powershell
# Python
ruff check src/ tests/

# TypeScript
cd desktop && npx eslint src/
```

## Core Principles

- **Safety first** — preview before destructive actions
- **Idempotent behavior** — already compliant files should be skipped
- **Traceable decisions** — date choice, skip reasons, and target paths stay explainable
- **Core/UI separation** — engine decisions in core; GUI consumes explicit contracts
- **Windows first** — Windows is the primary target
- **English first** — CLI output and JSON contracts in English

## Architecture

The desktop frontend is a **fresh redesign** (Tauri + React + TypeScript + shadcn/ui) under `./desktop`. The old PySide6 GUI has been removed. See [docs/ui-migration.md](docs/ui-migration.md).

### App Services
The CLI exposes headless app-service contracts for the GUI to consume without parsing console text:

```powershell
media-manager app manifest --json
media-manager app-services contracts --json
media-manager app-services review-workbench --json
media-manager app profiles list --profile-dir .\profiles --json
```

Run folders created with `--run-dir` include GUI-facing artifacts (`ui_state.json`, `plan_snapshot.json`, `action_model.json`) alongside `command.json`, `report.json`, and `summary.txt`.

## Scope

This is a core-first codebase with the CLI as the stable operational base and a controlled desktop GUI layer introduced through tested contracts, safer execution, clearer reporting, and repeatable workflow operations.
