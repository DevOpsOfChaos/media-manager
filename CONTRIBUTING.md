# Contributing

Thank you for your interest in contributing.

## Current project stage

This project is in a pre-alpha stage. The core logic is still being stabilized, and the user interface will evolve over time. Expect rough edges and breaking changes.

## Before opening an issue

Please:
- verify that you are using a recent version of the project
- check existing issues for duplicates
- include clear reproduction steps for bugs
- include operating system, Python version, and whether ExifTool is installed

## Before opening a pull request

Please:
- keep changes focused and narrow in scope
- avoid unrelated refactors
- document user-visible behavior changes
- add or update tests when logic changes
- make sure the test suite passes locally

## Development setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
pytest
```

## Style guidelines

- Prefer readable, explicit code over clever code
- Keep modules small and single-purpose
- Preserve separation between core logic and UI logic
- Avoid hardcoded local paths
- Keep platform-specific behavior isolated where possible

## Pull request checklist

- [ ] My change is focused and limited in scope
- [ ] I tested the change locally
- [ ] I added or updated tests where appropriate
- [ ] I updated documentation where needed
- [ ] I did not include private data, local binaries, or machine-specific paths
