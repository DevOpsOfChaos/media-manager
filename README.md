# Media Manager

[![Tests](https://github.com/DevOpsOfChaos/media-manager/actions/workflows/tests.yml/badge.svg)](https://github.com/DevOpsOfChaos/media-manager/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
[![License: MIT](https://img.shields.io/github/license/DevOpsOfChaos/media-manager)](LICENSE)

Open-source desktop foundation for organizing photos and videos by metadata and file dates.

> **Project status:** pre-alpha. The current focus is a reliable core, not feature breadth or polished UI.

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
- Resolve ExifTool through:
  - `PATH`
  - `EXIFTOOL_PATH`
  - an explicit CLI / GUI path
  - common Windows install paths
- Desktop GUI foundation
- CLI entry point
- Automated tests for core date and sorting logic

## Planned capabilities

- Template-based renaming
- Duplicate detection
- Flexible sorting rules and filters
- SQLite-backed media index
- Faster processing for large libraries
- Modern desktop UI
- Windows packaging / installer
- Releases

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

That is what makes it possible to start with a pragmatic Tkinter GUI now and later move to a more professional UI stack without rewriting the core behavior.

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
python -m media_manager organize "C:\Path\To\Unsorted" "C:\Path\To\Sorted"
```

CLI apply with copy:

```powershell
python -m media_manager organize "C:\Path\To\Unsorted" "C:\Path\To\Sorted" --apply --copy
```

CLI apply with move:

```powershell
python -m media_manager organize "C:\Path\To\Unsorted" "C:\Path\To\Sorted" --apply --move
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

## Tkinter note

If `python -m media_manager` ends with `No module named tkinter`, then the Python installation does not include Tkinter / Tcl-Tk support.

That does **not** mean the project is unusable. The CLI still works.  
It only means the current GUI entry point cannot start with that Python installation.

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

## Honest scope statement

This is not yet a finished public media manager. It is an early but structured foundation.

That distinction matters. Repositories rot when maintainers pretend an early base is already a product.
