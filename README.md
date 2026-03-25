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
- Resolve ExifTool through:
  - `PATH`
  - `EXIFTOOL_PATH`
  - an explicit CLI / GUI path
  - common Windows install paths
- PySide6 desktop GUI baseline
- Organizer dashboard-style summary cards and result table
- CLI entry point
- Automated tests for core date and sorting logic

## Planned capabilities

- Saved import sets for reusable folder groups
- Template-based renaming
- Duplicate detection
- Keep-source / keep-target / keep-both decisions for exact duplicates
- Visual comparison for images and videos
- Flexible sorting rules and filters
- SQLite-backed media index
- Faster processing for large libraries
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

Only the first area is actively implemented right now. The others are planned and should be built on top of the same core instead of becoming separate one-off tools.

## Architecture

```text
media-manager/
├── docs/
├── src/
│   └── media_manager/
│       ├── cli.py
│       ├── dates.py
│       ├── exiftool.py
│       ├── gui.py
│       └── sorter.py
├── tests/
├── pyproject.toml
└── README.md
```

The important rule is simple: **core logic stays separate from UI code**.

That is what makes it possible to improve the desktop UI later, add localization later, and eventually support saved import sets without rewriting the core behavior.

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

GUI:

```powershell
python -m media_manager
```

CLI preview:

```powershell
python -m media_manager organize --source "C:\Path\To\UnsortedA" --source "C:\Path\To\UnsortedB" --target "C:\Path\To\Sorted"
```

CLI apply with copy:

```powershell
python -m media_manager organize --source "C:\Path\To\UnsortedA" --source "C:\Path\To\UnsortedB" --target "C:\Path\To\Sorted" --apply --copy
```

CLI apply with move:

```powershell
python -m media_manager organize --source "C:\Path\To\UnsortedA" --source "C:\Path\To\UnsortedB" --target "C:\Path\To\Sorted" --apply --move
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
- [Contributing guide](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Support](SUPPORT.md)
- [v0.3 baseline protocol](docs/protocol/2026-03-25-v0.3-pyside6-multisource.md)
- [v0.3.1 organizer GUI polish protocol](docs/protocol/2026-03-25-v0.3.1-organizer-gui-polish.md)

## Honest scope statement

This is not yet a finished public media manager. It is an early but structured foundation.

That distinction matters. Repositories rot when maintainers pretend an early base is already a product.
