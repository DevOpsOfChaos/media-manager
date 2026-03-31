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
- [x] Exact-duplicate cleanup plan and dry-run foundation
- [x] Exact-duplicate execution preview foundation
- [x] Exact-duplicate execution runner baseline
- [x] Duplicate workflow CLI with session save/load
- [x] Duplicate engine startup self-test
- [x] Associated-file detection foundation
- [x] Associated-file safety blocking in duplicate delete path
- [x] Trash-based duplicate delete execution
- [x] Structured duplicate execution audit logging
- [ ] Keep-source / keep-target / keep-both actions
- [ ] Duplicate decision queue for larger batches
- [ ] Similarity pipeline for likely duplicates
- [ ] Rich associated-file execution handling beyond current safety blocking
- [ ] Duplicate dry-run / execution surface in the QML workflow UI

## Phase 4 — comparison workflows

- [ ] Image comparison view
- [ ] Video comparison view
- [ ] Metadata side-by-side view
- [ ] Fast keep / reject actions from the comparison screen
- [ ] Separation between exact duplicates and likely duplicates

## Phase 5 — guided product UX

- [x] Guided home page baseline
- [x] Workflow progress stepper baseline
- [x] Initial QML / Qt Quick shell for home + workflow
- [ ] Large questionnaire-first landing page refinement
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

- [x] Hidden workflow snapshot baseline
- [x] Exact-duplicate session snapshot persistence baseline
- [ ] Hidden workflow database inside target structures
- [ ] Crash-safe workflow recovery
- [ ] Resume and re-open prior optimized targets
- [ ] Decision persistence across sessions beyond current exact-duplicate baseline

## Phase 8 — productization

- [x] QML / Qt Quick migration for the primary workflow shell
- [ ] Modern desktop UI refinement
- [ ] Windows packaging
- [ ] Installer
- [ ] Signed releases
- [ ] Release notes and versioned changelog

## Reference documents

- `docs/product_vision.md`
- `docs/workflow_ux_target.md`
- `docs/65_exact_duplicate_feature_state.md`
