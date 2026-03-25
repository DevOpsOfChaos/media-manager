# Contributing

Thanks for contributing.

## Current project stage

This repository is still in pre-alpha. The core is being stabilized, the UI will evolve, and breaking changes are normal at this stage.

## Ground rules

- keep changes focused
- avoid unrelated refactors
- prefer small pull requests over large rewrites
- document user-visible behavior changes
- add or update tests when logic changes
- do not commit private data, local binaries, or machine-specific paths

## Before opening an issue

Please:

- verify that you are using a recent version of the repository
- check for existing duplicate issues
- include clear reproduction steps
- include operating system, Python version, and ExifTool details
- include the exact error or traceback when relevant

## Development setup

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
pytest
```

## Pull request checklist

- [ ] Change is limited in scope
- [ ] Change was tested locally
- [ ] Tests were added or updated where appropriate
- [ ] Documentation was updated where needed
- [ ] No private paths, private media, or local binaries were committed

## Conduct

By participating in this repository, you agree to follow the expectations described in `CODE_OF_CONDUCT.md`.
