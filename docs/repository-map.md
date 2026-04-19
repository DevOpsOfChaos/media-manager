# Repository Map

This document is the quickest way to understand where to look in the repository.

## Start here

If you are new to the repo, read these first:

1. `README.md`
2. `docs/status.md`
3. `docs/cli-workflows.md`
4. `docs/workflow-profiles-and-bundles.md`
5. `docs/roadmap.md`

## Top-level project docs

### `README.md`

High-level project overview, direction, and entry links.

### `CONTRIBUTING.md`

How to contribute, current expectations, and testing/documentation rules.

### `SUPPORT.md`

What kind of support requests are useful right now and what details to include.

### `SECURITY.md`

How to report security-sensitive issues privately.

## Direction and status docs

### `docs/status.md`

Best short truth snapshot of what the repository currently is.

### `docs/roadmap.md`

The intended order of work and major phases.

### `docs/architecture.md`

How the repository is layered and what should stay in core vs. workflow vs. GUI.

### `docs/transition/legacy-reset.md`

Why the repository was reset and how to think about older code.

## Product and usage docs

### `docs/cli-workflows.md`

Overview of the main CLI workflows and how they relate.

### `docs/workflow-profiles-and-bundles.md`

How presets, saved profiles, inventories, bundles, sync, compare, extract, and run flows fit together.

## Code areas to know

### `src/media_manager/`

Main package root.

Important current product-facing areas include:

- CLI entry modules
- core media logic
- state/history/journaling helpers
- workflow/profile/bundle helpers

### `src/media_manager/core/`

Core logic and product-facing helpers.

### `src/media_manager/core/workflows/`

Workflow layer, including:

- presets
- profile validation
- profile inventory
- profile bundles
- shell/form/launcher models

### `tests/`

Regression surface.

When changing behavior, do not look only at the one obvious new test. Many compatibility-sensitive behaviors are covered indirectly here.

## Suggested reading paths

### If you want to work on CLI/Core features

Read:

1. `README.md`
2. `docs/status.md`
3. `docs/architecture.md`
4. the relevant files under `src/media_manager/`
5. the matching tests under `tests/`

### If you want to work on workflows/profiles/bundles

Read:

1. `docs/workflow-profiles-and-bundles.md`
2. `docs/cli-workflows.md`
3. `docs/architecture.md`
4. `src/media_manager/core/workflows/`
5. matching `tests/test_*workflow*` files

### If you want to understand old vs. current direction

Read:

1. `docs/transition/legacy-reset.md`
2. `docs/architecture.md`
3. `docs/status.md`
