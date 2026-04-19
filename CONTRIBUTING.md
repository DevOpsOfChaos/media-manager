# Contributing

Thanks for contributing to **media-manager**.

This repository is in an active pre-release stage, but it is no longer just a vague reset. The project now has a growing CLI/Core surface around:

- scan and inspect
- date resolution
- organize and rename flows
- duplicate review and reporting
- trip and cleanup workflows
- workflow presets, saved profiles, and profile bundles

The current priority is still the same:

1. core reliability
2. CLI product quality
3. reporting, journaling, history, and repeatability
4. guided workflow layers
5. GUI later

## Project defaults

Use these defaults unless a change explicitly targets something else:

- **English first** for documentation, runtime messages, JSON field names, and CLI output
- **Windows first** for usability and path-handling expectations
- **CLI/Core before GUI** for new product work
- **Additive changes** over silent contract breaks

## What good contributions look like right now

Helpful contributions usually do at least one of these well:

- harden an existing CLI/Core feature
- improve reporting, diagnostics, or safety behavior
- extend tests without breaking older contracts
- reduce ambiguity in docs or examples
- make repeated workflows easier to review and rerun

Less helpful contributions right now are things like:

- broad GUI redesigns that bypass the core
- cosmetic rewrites with little product value
- changing JSON/text contracts without checking compatibility
- large architectural churn without a focused user-facing benefit

## Ground rules

- keep changes scoped and intentional
- avoid unrelated refactors in the same pull request
- prefer real product improvement over cosmetic code motion
- preserve existing JSON/text/test contracts when reasonably possible
- add or update tests when behavior changes
- document user-visible behavior changes
- do not commit private media, local binaries, secrets, or machine-specific paths

## Before opening an issue

Please include:

- operating system
- Python version
- whether ExifTool is installed and reachable
- the exact command you ran
- the full traceback or error text
- whether the problem happened in preview or apply mode
- whether it involves run logs, journals, workflow profiles, or bundles

## Development setup

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
pytest
```

## Testing expectations

Before you propose a change, try to check more than only the one new happy-path test.

Please pay special attention to these regression-sensitive areas:

- `__init__.py` exports
- legacy helpers that tests import directly
- JSON compatibility
- text-output compatibility
- SimpleNamespace-style or lightweight test doubles
- workflow profile / bundle / shell model wiring

If a change touches a broad CLI/Core contract, a good local check pattern is:

```powershell
pytest -q <targeted tests>
pytest -q
```

## Pull request checklist

- [ ] Change is limited in scope and intentional
- [ ] Local tests were run at the right level for the change
- [ ] Older compatibility-sensitive tests were considered where relevant
- [ ] Docs were updated where needed
- [ ] No private paths, private media, or local binaries were committed
- [ ] The change improves actual product behavior, not just code shape

## Documentation guidance

When you update docs, prefer:

- concrete examples over slogans
- current product truth over roadmap optimism
- explaining preview/apply/reporting behavior clearly
- linking related docs instead of duplicating everything everywhere

Start here if you are unsure where a doc belongs:

- `README.md`
- `docs/repository-map.md`
- `docs/cli-workflows.md`
- `docs/workflow-profiles-and-bundles.md`
- `docs/status.md`

## Conduct

By participating in this repository, you agree to follow the expectations described in `CODE_OF_CONDUCT.md`.
