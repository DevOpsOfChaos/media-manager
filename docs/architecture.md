# Architecture Notes

## Design goal

Keep media handling logic independent from the user interface.

That is the core rule that allows the project to evolve from a pragmatic Tkinter desktop app into a more professional UI without rewriting the sorting engine.

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

It should not become the place where business logic silently accumulates.

## Why this matters

Most small utility tools decay because the UI and the actual logic get fused together.  
Once that happens, every future UI change becomes expensive.

The current structure avoids that trap on purpose.

## Evolution path

The intended long-term direction is:

1. stabilize the current core
2. add real user-facing features
3. improve test coverage
4. replace the temporary GUI layer with a more modern UI stack
5. add packaging and releases
6. add optional localization without mixing translations into the core logic

## Non-goals for now

- broad refactors without user value
- premature plugin systems
- fake enterprise architecture
- pretending the project is further along than it is
