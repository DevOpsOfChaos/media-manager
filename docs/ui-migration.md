# UI Migration — PySide6 → Tauri + React

## Decision

The old PySide6 desktop UI has been removed. The future desktop UI is a
Tauri + React + TypeScript frontend under `./desktop`.

## Design approach — redesign from scratch

The new Tauri/React UI is a **fresh redesign**, not a visual or structural
port of the old PySide6/Qt GUI.

- **Do not recreate** old PySide6 screens, layouts, dialogs, widget
  hierarchies, or visual structure.
- Deleted PySide6 files (`gui_desktop_qt*.py`, `gui_review_workbench_qt.py`,
  `gui_similar_comparison_qt.py`, `gui_desktop_tk.py`, `gui_app.py`) are
  **historical reference only**. Their visual patterns should not be copied.
- Remaining `core/gui_qt_*` modules are **functional inventory and headless
  contract references only**. Their naming (`gui_qt_*`) is an artifact of
  the old architecture and does **not** imply a design direction.
  Use them to understand what data contracts exist, not how screens should
  look.

### New UI principles

- **Modern desktop-app patterns:** clear navigation/sidebar, dashboard
  overview, focused workflows, card/detail layouts.
- **Fewer modal dialogs.** Prefer inline panels, drawers, or dedicated
  pages over stacked modals.
- **Readable spacing and typography.** Follow shadcn/ui defaults.
- **Consistent design system** built on shadcn/ui + Tailwind CSS.
- **Backend workflows preserved:** scanning, duplicate detection,
  similar media review, decisions/actions, reports/history, settings.
- **English-first** product language.

### What to preserve from the old architecture

- Functional inventory: which backend operations exist and what they do.
- Data contracts: JSON schemas for reports, plans, reviews, run artifacts.
- Safety boundaries: preview-before-apply, confirmation gates, dry-run
  contracts.
- Workflow sequences: scan → plan → review → apply → journal → undo.

## Boundary

```
Python backend (src/media_manager/)          Tauri/React frontend (desktop/)
├── core/   — scanning, duplicates,       ├── src/   — React components
│             decisions, metadata,        ├── src-tauri/ — Rust shell
│             organizer, renamer,         └── public/
│             people, workflows
├── cli*.py — CLI entrypoints
└── (no UI imports)
```

- **Python core/CLI owns:** scanning, duplicate detection, decisions,
  file operations, reports, metadata extraction, people recognition,
  organizer, renamer, workflows.
- **Tauri/React owns:** desktop presentation, window management,
  navigation, UI state.
- **Integration:** through a stable backend boundary (future design).
  Do not import UI code into core. Do not import PySide6/Qt anywhere.
- **Headless core modules** under `core/gui_qt_*` are pure-data
  planning/blueprint modules. They do not import PySide6. They remain
  as reference designs for the new UI.

## What was removed

- `gui_desktop_qt_v2.py` — PySide6 GUI v2
- `gui_desktop_qt.py` — PySide6 GUI + headless wrappers
- `gui_review_workbench_qt.py` — Qt widget builder
- `gui_similar_comparison_qt.py` — Qt widget builder
- `gui_desktop_tk.py` — deprecated Tkinter shim
- `gui_app.py` — `media-manager-gui` entrypoint
- `gui`/`gui-qt` optional dependencies (PySide6)
- Tests that imported deleted modules

## What remains

- All CLI entrypoints (`media-manager`, `media-manager-app`, etc.)
- All core modules (scanner, organizer, renamer, people, workflows, etc.)
- Headless `gui_qt_*` blueprint modules in `core/` — pure data, no PySide6.
  **Functional inventory and contract reference only.** Not a design direction.
  The `gui_qt_*` naming prefix is a legacy artifact.
- `./desktop` — Tauri + React + TypeScript + shadcn/ui frontend (fresh redesign)
