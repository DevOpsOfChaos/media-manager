# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and the project aims to follow Semantic Versioning once regular public releases begin.

## [Unreleased]

### Added
- Public repository baseline files
- GitHub issue and pull request templates
- Automated test workflow
- Architecture notes
- Support guide
- Code of conduct
- Dependabot configuration
- PySide6 desktop baseline for the organizer workflow
- Multi-source folder support for the organizer workflow
- Implementation protocol for the v0.3 baseline
- Organizer dashboard-style summary cards and improved GUI layout
- Open-target-folder action in the organizer GUI
- Additional organizer tests for repeated source-path input
- Application settings persistence for organizer defaults
- App shell with a home page and organizer page
- Compact source-folder list with full-path details
- Live organizer progress feedback during processing
- Organizer test coverage for progress callback reporting

### Changed
- README rewritten to present the repository as a public project front door
- Roadmap rewritten for clearer public project direction
- Project metadata improved in `pyproject.toml`
- Test workflow expanded to Python 3.11 and 3.12
- `.gitignore` extended for common Python build and cache artifacts
- Repository and application default language standardized to English
- Core sorting configuration now supports multiple source folders
- CLI updated to use repeatable `--source` flags and explicit `--target`
- Organizer GUI refined with a cleaner app shell, less text, and more readable results
- Organizer GUI now auto-fills the ExifTool path when it can be resolved
- Organizer run flow now disables conflicting UI actions while processing
- Result-table columns now resize to content more aggressively and the status column is visually stronger

### Notes
- The project remains in pre-alpha.
- Breaking changes are still expected while the core feature set is being stabilized.
