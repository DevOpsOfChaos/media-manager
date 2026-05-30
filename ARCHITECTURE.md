# Architecture

## Layers
1. Tauri Shell (Rust) — Window management, IPC
2. Python Bridges — JSON stdin/stdout subprocess
3. Core Engine — Business logic
4. React Frontend — UI with shadcn/ui

## Data Flow
Frontend → invoke() → Rust Command → Python Bridge → Core → Result → JSON → Frontend

## Key Modules
- organizer/ — File organization into dated folders
- duplicates/ — Exact & similar duplicate detection
- people_recognition/ — Face detection & matching
- renamer/ — File renaming with patterns
- scanner/ — Media file discovery

## Tech Stack
- **Backend**: Python 3.11+ (core engine, CLI tools)
- **Desktop Shell**: Rust (Tauri v2)
- **Frontend**: React 19 + TypeScript + Tailwind CSS + shadcn/ui
- **Metadata**: ExifTool
- **Face Recognition**: dlib + face-recognition-models

## Project Structure
```
media-manager/
├── src/                    # Python core engine
│   └── media_manager/      # Main package
├── desktop/                # Tauri + React frontend
│   ├── src/                # React application
│   ├── src-tauri/          # Rust backend
│   └── package.json        # Node dependencies
├── tests/                  # Python test suite
├── pyproject.toml          # Python project config
├── ARCHITECTURE.md         # This file
└── CHANGELOG.md            # Release history
```

## CLI Entry Points
All operations are available as standalone CLI commands (media-manager-*) that communicate via JSON stdin/stdout. The Tauri desktop app calls these same commands through IPC, ensuring consistent behavior between CLI and GUI.

## Testing
- Python: pytest (1350+ tests)
- Frontend: TypeScript strict mode validation via `tsc --noEmit`
