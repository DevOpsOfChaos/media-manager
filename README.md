# Media Manager

[![Tests](https://github.com/DevOpsOfChaos/media-manager/actions/workflows/tests.yml/badge.svg)](https://github.com/DevOpsOfChaos/media-manager/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
[![License: MIT](https://img.shields.io/github/license/DevOpsOfChaos/media-manager)](LICENSE)

Open-source media organization software for photos and videos.

> **Project status:** repository reset in progress.
>
> This repository is being re-founded around a stable core, a clear CLI, safe planning flows, and a later GUI. Some older desktop-oriented code still exists in the repository and should currently be treated as **legacy reference**, not as the product direction.

## Project language

English is the default language for:

- repository documentation
- issues and pull requests
- application UI and runtime messages

Additional localizations may be added later. German is a likely secondary language, but it is not the default.

## Why this repository exists

The project started from a script that already handled media sorting reasonably well.

The long-term goal is much larger:

- organize photos and videos from one or more source folders
- resolve capture dates more reliably
- rename files using user-controlled templates
- detect exact duplicates safely
- later detect likely duplicates for review
- support guided workflows such as cleanup and trip collections

The repository is now being reset so these capabilities grow from a reliable foundation instead of from UI-first experiments.

## Current direction

The project is being rebuilt in this order:

1. **Core foundation**
2. **CLI workflows**
3. **State and idempotent processing**
4. **Duplicate handling**
5. **Guided workflows**
6. **Modern GUI later**

That order is deliberate.

A polished interface does not matter if capture-date resolution, planning, skip behavior, duplicate handling, and safety rules are still weak.

## Core principles

- **Safety first** — preview before destructive actions
- **Idempotent behavior** — already compliant files should be skipped
- **Traceable decisions** — the program should explain why it used a date, skipped a file, or planned a target path
- **Core/UI separation** — the media engine must stay independent from the interface
- **Windows first** — Windows is the primary target for the early stable milestones
- **English first** — localization can be layered in later

## Planned feature groups

### Organize

- process one or more source folders
- resolve the best available capture date
- build target folder structures safely
- move, copy, or link depending on workflow and user choice

### Rename

- preview rename plans
- support composable naming templates
- avoid collisions safely

### Duplicates

- exact duplicate detection first
- later similarity-based review for likely duplicates
- quarantine / review flow instead of unsafe bulk deletion

### Workflows

- cleanup workflow for unsorted mixed sources
- trip workflow for time-range-based collections
- guided step-by-step execution built on the same core

## Legacy notice

This repository contains older implementation directions that are no longer the architectural target.

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

## Development state

The repository should currently be understood as:

- an active reset
- not a finished product
- not yet feature-complete
- intentionally moving away from premature UI expansion

That honesty matters more than pretending the repository is already a polished media manager.

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

This is not yet a finished public media manager.

It is a project being reset onto a stronger architectural foundation so the later open-source product can actually become trustworthy.
