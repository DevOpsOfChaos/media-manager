# GUI Shell Scaffold v1

This block introduces the first new UI-oriented shell for the rebuilt media-manager project.

## Goal

Provide a lightweight new desktop entry point that helps users discover workflows and copy command previews,
without forcing the project back into a GUI-first architecture.

## What is included

- a new `media-manager shell` command
- a headless model mode with `--dump-model`
- workflow and problem preview modes
- an optional PySide6-powered desktop window when GUI dependencies are installed

## Important scope boundary

This is **not** the final modern GUI.

It is a scaffold that sits on top of the rebuilt CLI and workflow catalog:

- discover workflows
- inspect problem-oriented recommendations
- copy command previews
- prepare for later richer GUI integration

## Example commands

```bash
media-manager shell --dump-model
media-manager shell --preview-workflow cleanup
media-manager shell --preview-problem build-trip-collection
media-manager shell
```

## Why this step matters

The project now has enough workflow and state infrastructure that a new user-facing shell can finally sit on top
of real functionality instead of legacy-only surfaces.
