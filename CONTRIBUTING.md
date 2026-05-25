# Contributing to Media Manager

Thanks for your interest! Media Manager is a local-first media workflow assistant built with Python, Rust, and React.

## Quick Start

```bash
# Clone and install
git clone https://github.com/mries/media-manager.git
cd media-manager

# Python backend
pip install -e ".[dev]"

# Desktop frontend
cd desktop
npm ci
```

## Development

- **Python**: Core engine, CLI, bridges → `src/media_manager/`
- **React/TS**: Desktop frontend → `desktop/src/`
- **Rust**: Tauri shell → `desktop/src-tauri/`
- **Tests**: `tests/` (run with `pytest tests/ -x --tb=short -q`)

## Before submitting

```bash
make check  # runs lint + typecheck + tests
```

## Project structure

- `cli.py` — root CLI dispatcher (15 commands)
- `cli_organize.py` — file organization into date-based folders
- `cli_duplicates.py` — exact & similar duplicate detection
- `cli_people.py` — face recognition & person catalog
- `cli_trip.py` — trip/event collections
- `core/` — shared engine (organizer, scanner, media groups, people recognition)
- `bridge_*.py` — JSON IPC bridges for Tauri desktop

## License

MIT — see [LICENSE](LICENSE)
