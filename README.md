# Media Manager

[![Tests](https://github.com/DevOpsOfChaos/media-manager/actions/workflows/tests.yml/badge.svg)](https://github.com/DevOpsOfChaos/media-manager/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
[![License: MIT](https://img.shields.io/github/license/DevOpsOfChaos/media-manager)](LICENSE)

Open-source media organization software for photos and videos.

> **Project status:** active core/CLI build.
>
> The repository is currently being shaped into a reliable media-management core with a practical CLI, review-safe workflows, reusable profiles, and a later GUI on top. The product direction is intentionally **core first, CLI first, Windows first, English first**.

## Project language

English is the default language for:

- repository documentation
- issues and pull requests
- application UI and runtime messages
- JSON fields and CLI-facing output

Additional localizations may be added later. German is a likely secondary language, but it is not the default.

## Product direction

The repository is being built in this order:

1. core foundation
2. CLI commands and safe preview/apply flows
3. state, journaling, history, and undo
4. duplicate and similar-media review
5. workflow helpers, reusable profiles, and profile bundles
6. GUI later

That order is deliberate.

A polished interface does not matter if capture-date resolution, planning, conflict handling, duplicate review, and safety rules are still weak.

## Current capability snapshot

The current CLI-first product line centers on:

- metadata/date inspection and date-resolution diagnostics
- organize and rename planning/apply flows
- exact duplicate review and similar-review helpers
- workflow history, journaling, and undo-oriented reporting
- guided workflow entry points such as cleanup and trip
- reusable workflow presets and saved profiles
- profile inventory, audit, batch execution, and bundle roundtrips

The workflow/profile layer is no longer just scaffolding. It is becoming a real productivity layer over the core CLI commands.

## Core principles

- **Safety first** — preview before destructive actions
- **Idempotent behavior** — already compliant files should be skipped
- **Traceable decisions** — the program should explain why it used a date, skipped a file, or planned a target path
- **Core/UI separation** — the media engine must stay independent from the interface
- **Windows first** — Windows is the primary target for the early stable milestones
- **English first** — localization can be layered in later

## Workflow layer

The workflow CLI now covers more than just “run one workflow”.

Examples:

```powershell
media-manager workflow presets
media-manager workflow render-preset cleanup-family-library --source C:\Photos --source D:\Phone --target E:\Library
media-manager workflow profile-save .\profiles\family-cleanup.json --preset cleanup-family-library --source C:\Photos --source D:\Phone --target E:\Library
media-manager workflow profile-list --profiles-dir .\profiles
media-manager workflow profile-run-dir --profiles-dir .\profiles --only-valid
media-manager workflow profile-bundle-write .\bundles\profiles.json --profiles-dir .\profiles
media-manager workflow profile-bundle-run .\bundles\profiles.json --only-valid
media-manager workflow profile-bundle-sync .\bundles\profiles.json --target-dir .\profiles-restored --apply
```

See also:

- [Workflow CLI guide](docs/cli-workflows.md)
- [Workflow profiles and bundles](docs/workflow-profiles-and-bundles.md)
- [Current development status](docs/status.md)

## Legacy notice

The repository still contains older implementation directions that are no longer the architectural target.

Examples include earlier GUI-heavy and desktop-first iterations. They may still contain useful code or ideas, but they should be treated as reference material while the new core-first structure is established.

See:

- `docs/transition/legacy-reset.md`
- `legacy/README.md`
- `docs/architecture.md`
- `docs/roadmap.md`

## Requirements

- Windows is the primary target right now
- Python 3.11+
- ExifTool

## Development

Run tests:

```powershell
pytest -q
```

See also:

- [Roadmap](docs/roadmap.md)
- [Architecture notes](docs/architecture.md)
- [Workflow CLI guide](docs/cli-workflows.md)
- [Workflow profiles and bundles](docs/workflow-profiles-and-bundles.md)
- [Current status](docs/status.md)
- [Contributing guide](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Support](SUPPORT.md)

## Honest scope statement

This is not yet a finished public media manager.

It is a serious CLI/core-first rebuild aimed at becoming a trustworthy media-management product rather than a UI-first prototype with fragile internals.
