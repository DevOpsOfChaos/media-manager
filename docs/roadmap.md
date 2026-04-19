# Roadmap

## Direction

The current product strategy is:

1. core foundation
2. CLI quality and safe apply flows
3. state / journaling / history / undo
4. duplicates and similar-review hardening
5. workflow presets / profiles / bundles
6. GUI later

This roadmap intentionally reflects the **current working direction**, not the older reset text alone.

## What is already in place

### Core and scan/date foundation

Available now in the active CLI/core line:

- media scanning across one or more source folders
- capture-date resolution with diagnostics and reasons
- inspect/metadata visibility for debugging and trust
- filename and filesystem fallbacks where metadata is weak

### Organize / rename / history basics

Available now in the active CLI/core line:

- organize preview/apply flows
- rename preview/apply flows
- journaling and run-log support
- history summaries and command-filtered history views
- undo-oriented reporting and state helpers

### Duplicates and review layer

Available now in the active CLI/core line:

- exact-duplicate review paths
- similar-review oriented workflow support
- duplicate planning/reporting helpers
- safer review-first direction instead of blind destructive execution

### Workflow productivity layer

Available now in the active CLI/core line:

- workflow discovery / recommendation / wizard helpers
- built-in workflow presets
- saved workflow profiles
- profile validation, inventory, audit, and directory execution
- profile bundles for write / show / audit / merge / compare / extract / sync / run
- shell/form/launcher models that understand presets and profiles better

## Current hardening priorities

These are the areas that deserve the most attention next.

### 1. CLI/core product hardening

- broader regression checks before every ZIP/commit
- fewer compatibility slips across `__init__` exports and helper imports
- preserve older JSON/text contracts unless there is a deliberate migration
- keep Windows path behavior explicitly tested

### 2. Media workflows people actually use

- strengthen organize/rename reporting and journaling consistency
- keep duplicate and similar-review flows easy to inspect before apply
- continue reducing friction for repeatable workflows built from saved profiles

### 3. Workflow/profile/bundle ergonomics

- make profile and bundle operations easier to document and maintain
- keep bundle/profile commands internally consistent
- avoid duplicating inventory/filter/summary logic in multiple layers

## Not the main focus right now

The following are intentionally not first-priority:

- polishing desktop visuals before the CLI/core stabilizes
- reintroducing GUI-first product decisions
- pretending the repository is already a finished end-user app
- unsafe destructive flows without reviewable reporting

## Near-term next-step ideas

Good next larger blocks include:

- repo maintenance and documentation consolidation
- workflow/profile import/export polish
- organize/rename/duplicate reporting quality improvements
- cleanup workflow hardening on top of the now-stronger profile/bundle layer
