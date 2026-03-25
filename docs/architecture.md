# Architecture Notes

## Design goal

Keep media handling logic independent from the user interface.

That is the core rule that allows the project to evolve from the current organizer baseline into a more complete and more professional desktop application without rewriting the sorting engine.

## Current layers

### 1. Core logic

Core behavior lives in modules such as:

- `dates.py`
- `exiftool.py`
- `sorter.py`

This layer should decide:

- how dates are resolved
- how media files are classified
- where files should go
- how collisions are handled
- how multiple source folders are processed

This layer should **not** know anything about buttons, windows, or widget state.

### 2. CLI layer

`cli.py` exposes the core logic in a script-friendly interface.

This is useful for:

- testing
- automation
- debugging
- environments where the GUI is unavailable

### 3. GUI layer

`gui.py` is the current desktop entry point.

Its job is only to:

- collect user input
- call core behavior
- display results and errors
- manage application-level presentation state

It should not become the place where business logic silently accumulates.

### 4. Settings layer

`settings.py` stores lightweight application defaults such as the ExifTool path or target folder.

This layer should remain small and focused. It is not a substitute for future project data models such as saved import sets.

## Product modules

The long-term product direction is better understood as four modules built on one core:

1. **Organize**
2. **Rename**
3. **Duplicates**
4. **Compare**

The current repository implements the **Organize** baseline only.

## Why this matters

Most small utility tools decay because the UI and the actual logic get fused together.  
Once that happens, every future UI change becomes expensive.

The current structure avoids that trap on purpose.

## Evolution path

The intended long-term direction is:

1. stabilize the current core
2. expand the organizer flow with better user-facing controls
3. add reusable import sets for source-folder groups
4. add duplicate detection and duplicate decisions
5. add visual comparison workflows for images and videos
6. improve test coverage
7. refine the desktop UI
8. add optional localization without mixing translations into the core logic
9. add packaging and releases

## Non-goals for now

- broad refactors without user value
- premature plugin systems
- fake enterprise architecture
- pretending the project is further along than it is
