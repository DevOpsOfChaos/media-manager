# Roadmap

## Reset principle

The repository is being reset around a stable media core.

That means the roadmap order is now:

1. core
2. CLI
3. state
4. duplicates
5. workflows
6. GUI later

## Phase 1 — repository reset and cleanup

- [x] keep the existing repository name
- [x] keep repository history
- [x] document that the repository is being reset
- [x] rewrite the public project direction around the core-first plan
- [x] add explicit legacy guidance
- [ ] freeze or relocate legacy-oriented files as the reset continues

## Phase 2 — scan and inspect baseline

- [ ] implement a clean scanner module
- [ ] support multiple source folders
- [ ] add an inspect command for metadata and date debugging
- [ ] report all relevant date candidates for a file
- [ ] make ExifTool integration observable and debuggable

## Phase 3 — date resolution baseline

- [ ] create a dedicated date resolver module
- [ ] support prioritized metadata tags
- [ ] support filename-based date extraction as a fallback
- [ ] support filesystem fallback as a last resort
- [ ] record source, confidence, and reasoning for the chosen date
- [ ] improve handling of video / QuickTime date edge cases

## Phase 4 — organize baseline

- [ ] build dry-run planning first
- [ ] support move, copy, and link-aware workflows where appropriate
- [ ] support configurable target folder structures
- [ ] improve collision handling
- [ ] add explicit skip reasons for already compliant files

## Phase 5 — rename baseline

- [ ] build composable naming templates
- [ ] preview rename plans before apply
- [ ] support text blocks and date-format blocks
- [ ] detect and handle rename collisions safely
- [ ] avoid renaming already compliant files

## Phase 6 — state and idempotence

- [ ] add a lightweight state store
- [ ] track file fingerprints and prior actions
- [ ] support rerun-safe behavior
- [ ] support clear skip explanations
- [ ] prepare the basis for undo and journaling

## Phase 7 — duplicates

- [ ] exact duplicate detection
- [ ] review-safe duplicate grouping
- [ ] quarantine-oriented actions instead of unsafe deletion
- [ ] similar-image duplicate detection after the exact pipeline is stable

## Phase 8 — workflows

- [ ] cleanup workflow for messy multi-source collections
- [ ] trip workflow using date ranges and collection output
- [ ] shared workflow state and reporting
- [ ] guided step-by-step execution built on the same core actions

## Phase 9 — GUI later

- [ ] design a modern interface on top of the stable core
- [ ] keep the GUI thin and workflow-oriented
- [ ] avoid reintroducing business logic into presentation code
- [ ] package a stable Windows release later

## Scope guardrails

The following are intentionally not first-priority during the reset:

- polishing desktop visuals before the core stabilizes
- growing multiple UI stacks in parallel
- pretending the product is further along than it is
- deleting media without a reviewable safety path
