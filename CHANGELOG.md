# Changelog

All notable changes to Media Manager.

## [Unreleased]

### Added
- Magic bytes detection: identify file types by content signature (ignores extension)
- Deep metadata extraction: EXIF, IPTC, XMP, MakerNotes with completeness scoring
- Auto-tagging engine: generate semantic tags from camera, date, GPS, ISO, focal data
- File health checker: detect corrupted/truncated JPEGs (missing SOI/EOI) and PNGs (missing IEND)
- Smart album suggestions: date-cluster and camera-based album groupings from metadata
- 18 new bridge commands for Tauri desktop integration (deep-meta, auto-tag, health, smart-albums, magic)
- Workflow runner page: run organize → duplicates in one sequence
- Face timeline page: browse photos of a person over time
- Quick-rename with batch-export support
- Dark mode theme
- Face recognition 2.0 with improved accuracy
- Onboarding wizard for first-time users
- 3-step organize wizard with success page
- Hardlink support for organize operations
- Pause/Resume for long-running operations via job queue
- Date source control (`--date-source` to pick EXIF/fs/name)
- Face recognition: ignore list, person merge, training feedback mode
- Custom tags + color labels + star ratings (sidecar/catalog)
- Smart collections: auto-updating rule-based collections
- Mini-mode / window shrink for compact library browsing
- Job queue system with status tracking and history
- CLI: `watch`, `stats`, `config`, `jobs` commands
- Workflow presets, profiles, and profile bundles
- App-service contracts and review workbench headless API
- Duplicate review with export/import decision files
- Similar image scanning with perceptual hashing
- Trip collections with date filtering
- Run history with structured JSON artifacts
- Doctor command for preflight validation
- Bachelor XML export for donation
- UI-polish: page-enter animations, smooth scroll navigation, card hover effects
- Button loading states across all submit forms
- Context-appropriate icons on empty state views

### Changed
- Desktop UI redesigned from scratch (Tauri + React + TypeScript + shadcn/ui)
- Removed old PySide6 GUI; new frontend under `./desktop`
- Bridge modules unified across CLI and Tauri IPC
- Organize preview: 10x faster for large libraries
- Library stability improvements: lazy images, crash fixes
- Thumbnail rendering with batch loading and retry logic
- UX overhaul: language-first onboarding, tool guides, favorites

### Fixed
- EXIF date detection: 22 EXIF tags + Windows creation date fallback
- ExifTool group prefix bug causing dates to be missed
- Window resize now properly shrinks entire Tauri window via Rust backend
- Duplicate label rendering
- Pagination bug + responsive filters
- Dashboard crash: removed auto Python calls on mount
- Library crash 0xe0000008: GPU pipeline hardening
- Slideshow crash on large libraries
- 22 bugs fixed in expert agent sweep
- 12 issues fixed in 5-agent expert audit
- CI: use `python -m pytest` instead of bare pytest
- 8 UX fixes across 15 files in phase 3 audit
- Progress hook for duplicate scan with live feedback

### Performance
- 166k file performance optimization
- Bridge unification + memory optimizations
- Batch thumbnails + advanced filter performance
- Duplicate scan with live progress and multi-phase feedback
- 1-hour optimization blitz across 5 agents (1350 tests)
