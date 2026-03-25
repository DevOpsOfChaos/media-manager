# Roadmap

## Phase 1 — stable organizer foundation

- [x] Preserve working metadata-based sorting logic
- [x] Add dry-run and safer execution flow
- [x] Add automated tests for core logic
- [x] Separate core logic from UI-specific code
- [x] Switch the desktop baseline to PySide6
- [x] Support multiple source folders and one target folder
- [x] Improve the organizer GUI layout and feedback loop
- [x] Add a basic app shell with a home page and an organizer page

## Phase 2 — better organizer workflow

- [x] Auto-fill and persist organizer defaults where useful
- [x] Saved import sets for reusable source-folder groups
- [x] Template-based renaming baseline
- [ ] Flexible sorting rules
- [ ] Exclusion rules and filters
- [ ] Better conflict handling and reporting

## Phase 3 — duplicate handling

- [x] Exact duplicate detection via hashing / byte identity
- [x] Guided duplicate review baseline
- [ ] Keep-source / keep-target / keep-both actions
- [ ] Duplicate decision queue for larger batches
- [ ] Similarity pipeline for likely duplicates
- [ ] Associated file detection and handling

## Phase 4 — comparison workflows

- [ ] Image comparison view
- [ ] Video comparison view
- [ ] Metadata side-by-side view
- [ ] Fast keep / reject actions from the comparison screen
- [ ] Separation between exact duplicates and likely duplicates

## Phase 5 — guided product UX

- [x] Guided home page baseline
- [x] Workflow progress stepper baseline
- [ ] Large questionnaire-first landing page
- [ ] Full-page workflow steps instead of utility-panel layout
- [ ] Persistent bottom information bar with rotating tips
- [ ] Animated confirmations and transitions
- [ ] Stronger bilingual UX pass

## Phase 6 — sorting and rename system expansion

- [ ] Rich folder-structure builder
- [ ] Rich rename block builder
- [ ] More preset templates
- [ ] Preview examples for sorting and renaming
- [ ] Optional trip/session sorting entry point

## Phase 7 — persistence and resumability

- [ ] Hidden workflow database inside target structures
- [ ] Crash-safe workflow recovery
- [ ] Resume and re-open prior optimized targets
- [ ] Decision persistence across sessions

## Phase 8 — productization

- [ ] QML / Qt Quick migration for the primary UI
- [ ] Modern desktop UI refinement
- [ ] Windows packaging
- [ ] Installer
- [ ] Signed releases
- [ ] Release notes and versioned changelog

## Reference documents

- `docs/product_vision.md`
- `docs/workflow_ux_target.md`
