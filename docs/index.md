# Documentation Index

This page is the fastest way to find the right documentation for the current repository direction.

## Start here

Read these first if you are orienting yourself in the current repo:

1. `README.md`
2. `docs/status.md`
3. `docs/architecture.md`
4. `docs/cli-workflows.md`
5. `docs/workflow-history.md`
6. `docs/workflow-profiles-and-bundles.md`
7. `docs/repository-map.md`

## Direction and status

### `docs/status.md`

Best short snapshot of what the project currently is and what it is not.

### `docs/roadmap.md`

High-level order of work and intended phases.

### `docs/architecture.md`

How the repo is layered and where code should live.

### `docs/transition/legacy-reset.md`

Why older GUI-heavy or reset-era code should not be treated as the main direction.

## CLI and product usage

### `docs/cli-workflows.md`

Overview of the workflow-oriented CLI surface, including discovery, profiles, bundles, and history commands.

### `docs/workflow-history.md`

History-focused guide for logs, journals, audit filters, latest-per-command views, and summary helpers.

### `docs/workflow-profiles-and-bundles.md`

How presets, saved profiles, inventories, bundles, sync, compare, extract, and run flows fit together.

## Repository navigation

### `docs/repository-map.md`

Quick map for where to look in top-level docs, source areas, and tests.

## Contribution and support

### `CONTRIBUTING.md`

Contribution expectations, testing habits, and repo hygiene notes.

### `SECURITY.md`

Security reporting path.

### `SUPPORT.md`

How to ask for useful help and what details to include.

## Suggested reading paths

### If you want to work on CLI/Core

Read:

1. `README.md`
2. `docs/status.md`
3. `docs/architecture.md`
4. `docs/cli-workflows.md`
5. `docs/workflow-history.md`
6. the matching files under `src/media_manager/`
7. the matching files under `tests/`

### If you want to work on workflows, profiles, or bundles

Read:

1. `docs/cli-workflows.md`
2. `docs/workflow-history.md`
3. `docs/workflow-profiles-and-bundles.md`
4. `docs/repository-map.md`
5. `src/media_manager/core/workflows/`
6. matching `tests/test_*workflow*` files

### If you want to understand history, journaling, and undo

Read:

1. `docs/workflow-history.md`
2. `docs/architecture.md`
3. `src/media_manager/core/state/`
4. matching `tests/test_core_*history*`, `tests/test_core_execution_journal.py`, and `tests/test_core_undo.py`

### If you want to understand old vs. current direction

Read:

1. `docs/transition/legacy-reset.md`
2. `docs/architecture.md`
3. `docs/status.md`
4. `README.md`
