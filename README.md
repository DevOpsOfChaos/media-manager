# Media Manager

[![Tests](https://github.com/DevOpsOfChaos/media-manager/actions/workflows/tests.yml/badge.svg)](https://github.com/DevOpsOfChaos/media-manager/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
[![License: MIT](https://img.shields.io/github/license/DevOpsOfChaos/media-manager)](LICENSE)

Open-source desktop foundation for organizing photos and videos by metadata and file dates.

> **Project status:** pre-alpha. The current focus is a reliable core, not feature breadth or polished UI.

## Project language

English is the default language for:

- repository documentation
- issues and pull requests
- application UI and runtime messages

Additional localizations may be added later. German is a likely secondary language, but it is not the default.

## Why this repository exists

The project started from a script that already handled media sorting well.  
The real deficit was everything around it: project structure, safer execution, clearer setup, testability, and a path toward a real desktop application.

This repository fixes that foundation first.

## Current capabilities

- Sort photos and videos by metadata date
- Fall back to filesystem timestamps when metadata is missing
- Dry-run preview before applying changes
- Copy or move files
- Detect filename collisions
- Organize from multiple source folders into one target folder
- Save, load, and delete reusable import sets for organizer source/target combinations
- Rename media files in place from one or more source folders
- Preview rename plans before applying them
- Detect exact duplicates via hashing and byte identity
- Store exact-duplicate keep decisions in reusable session snapshots
- Build exact-duplicate cleanup plans, dry-runs, and execution previews
- Execute exact-duplicate delete rows through a guarded trash-based runner
- Block duplicate delete execution when associated files or stale scan conditions are detected
- Run a duplicate-engine startup self-test automatically
- Write structured duplicate execution audit logs
- Expose duplicate workflow operations through `media-manager-duplicates`
- Resolve ExifTool through:
  - `PATH`
  - `EXIFTOOL_PATH`
  - an explicit CLI / GUI path
  - common Windows install paths
- Auto-fill and persist organizer defaults such as ExifTool path and target folder
- PySide6 app shell with Home, Organize, and Rename workspaces
- Guided QML workflow shell with source/target setup, duplicate review foundation, sorting foundation, and rename foundation
- More compact organizer UI with reduced text noise
- Live organizer and rename progress feedback during runs
- Readable result tables with content-based column sizing
- CLI entry points for organize and duplicates workflows
- Automated tests for core date, sorting, rename, duplicate, and settings logic

## Planned capabilities

- Keep-source / keep-target / keep-both actions for duplicate resolution
- Duplicate decision queue for larger batches
- Similarity pipeline for likely duplicates
- Rich associated-file execution handling beyond current safety blocking
- Flexible sorting rules and filters
- Faster processing for large libraries
- Stronger duplicate and execution surfaces in the QML workflow UI
- Modern desktop UI refinement
- Optional localization with language switching
- Windows packaging / installer
- Releases

## Product direction

The current product shape is easiest to think about as four user-facing areas:

1. **Organize**
2. **Rename**
3. **Duplicates**
4. **Compare**

The first two areas are the most visible in the GUI right now.  
The duplicate area already has substantial backend, CLI, and safety work, but its final GUI surface is still incomplete.

## Architecture

```text
media-manager/
├── docs/
├── src/
│   └── media_manager/
│       ├── associated_files.py
│       ├── cli.py
│       ├── cli_duplicates.py
│       ├── cleanup_plan.py
│       ├── dates.py
│       ├── duplicate_session_store.py
│       ├── duplicate_startup_selftest.py
│       ├── duplicate_workflow.py
│       ├── duplicates.py
│       ├── execution_audit.py
│       ├── execution_plan.py
│       ├── execution_runner.py
│       ├── execution_safety.py
│       ├── exiftool.py
│       ├── gui.py
│       ├── qml_app.py
│       ├── renamer.py
│       ├── settings.py
│       └── sorter.py
├── tests/
├── pyproject.toml
└── README.md
```

The important rule is simple: **core logic stays separate from UI code**.

That is what makes it possible to improve the desktop UI later, add localization later, and eventually support duplicate and compare workflows without rewriting the core behavior.

## Requirements

- Windows is the primary target right now
- Python 3.11+
- ExifTool

## Quick start

```powershell
git clone https://github.com/DevOpsOfChaos/media-manager.git
cd media-manager
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
pytest
```

## Run the application

QML app:

```powershell
media-manager-qml
```

Fallback app:

```powershell
python -m media_manager
```

CLI organize preview:

```powershell
python -m media_manager organize --source "C:\Path\To\UnsortedA" --source "C:\Path\To\UnsortedB" --target "C:\Path\To\Sorted"
```

CLI organize apply with copy:

```powershell
python -m media_manager organize --source "C:\Path\To\UnsortedA" --source "C:\Path\To\UnsortedB" --target "C:\Path\To\Sorted" --apply --copy
```

CLI organize apply with move:

```powershell
python -m media_manager organize --source "C:\Path\To\UnsortedA" --source "C:\Path\To\UnsortedB" --target "C:\Path\To\Sorted" --apply --move
```

CLI duplicate workflow with plan output:

```powershell
media-manager-duplicates --source "C:\Path\To\Library" --policy first --mode delete --show-plan
```

CLI duplicate workflow with audit log:

```powershell
media-manager-duplicates --source "C:\Path\To\Library" --policy first --mode delete --show-plan --audit-log ".\duplicate-audit.json"
```

## ExifTool

ExifTool must actually exist on the machine. Pointing to a non-existent path is not configuration, it is fiction.

The project can detect ExifTool automatically in common situations.  
If needed, set it explicitly:

```powershell
$env:EXIFTOOL_PATH = "C:\Program Files\exiftool\exiftool.exe"
```

Known legacy Windows paths from the original script:

- `C:\Program Files\exiftool\exiftool.exe`
- `C:\Program Files\exiftool\exiftool(-k).exe`

## PySide6 note

The current desktop GUI is based on PySide6. If `python -m media_manager` reports that `PySide6` is unavailable, reinstall project dependencies:

```powershell
pip install -e ".[dev]"
```

## Development

Run tests:

```powershell
pytest
```

See also:

- [Roadmap](docs/roadmap.md)
- [Architecture notes](docs/architecture.md)
- [Exact duplicate feature state](docs/65_exact_duplicate_feature_state.md)
- [Contributing guide](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Support](SUPPORT.md)
- [v0.3 baseline protocol](docs/protocol/2026-03-25-v0.3-pyside6-multisource.md)
- [v0.3.1 organizer GUI polish protocol](docs/protocol/2026-03-25-v0.3.1-organizer-gui-polish.md)
- [v0.3.2 app shell and readability protocol](docs/protocol/2026-03-25-v0.3.2-app-shell-and-readability.md)
- [v0.3.3 processing feedback and table sizing protocol](docs/protocol/2026-03-25-v0.3.3-processing-feedback-and-table-sizing.md)
- [v0.3.4 import sets protocol](docs/protocol/2026-03-25-v0.3.4-import-sets.md)
- [v0.3.5 rename baseline protocol](docs/protocol/2026-03-25-v0.3.5-rename-baseline.md)

## Honest scope statement

This is not yet a finished public media manager. It is an early but structured foundation.

That distinction matters. Repositories rot when maintainers pretend an early base is already a product.
