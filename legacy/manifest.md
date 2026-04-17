# Legacy Manifest

This document lists repository areas that should currently be treated as **legacy-oriented surfaces** during the core-first reset.

They are not necessarily useless.

They are simply **not the active architectural driver anymore**.

## Confirmed legacy-oriented entry surfaces

- `src/media_manager/cli_gui.py`
- `src/media_manager/gui.py`
- `src/media_manager/gui_workflow.py`
- `src/media_manager/qml_app.py`
- `media-manager-gui` entry point
- `media-manager-qml` entry point

## Why these are marked legacy

These files and entry points are centered on desktop/UI behavior and were introduced before the underlying core, state, idempotence, and workflow architecture had stabilized enough.

That does not make them wrong as experiments.

It does make them the wrong place to keep driving the repository from.

## Current policy

- keep them runnable only when explicitly requested
- do not let them dictate new architecture
- salvage reusable ideas only when they fit the reset
- avoid expanding them as if they were the new baseline

## Transitional note

Some non-GUI flat modules still remain in place while the new core structure is introduced.

This repository is currently in a staged reset, not an instant rewrite.
