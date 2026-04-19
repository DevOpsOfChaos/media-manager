# Architecture Notes

## Design goal

Build a trustworthy media-management core first, and keep interfaces thin.

The repository now has more real CLI/product surface than an early reset snapshot suggests, but the architectural rule is unchanged:

- core decides behavior
- CLI exposes behavior clearly
- workflow/profile/bundle layers help compose behavior
- GUI comes later and should stay thinner than the CLI layer, not thicker

## Current active layers

### 1. Core media logic

This layer is responsible for:

- discovering media files
- reading metadata through ExifTool and related inspection paths
- resolving the best available capture date
- planning organization and renaming actions
- detecting exact duplicates and supporting review-oriented duplicate flows
- building workflow-level reports and summaries

This layer must stay independent from GUI concerns.

### 2. State, history, and journaling

This layer is responsible for:

- run logs
- execution journals
- workflow history scanning and summaries
- undo-oriented data capture
- repeatability and explainable reruns

The exact internal shape can still evolve, but the direction is clear: actions should become easier to inspect, review, and rerun safely.

### 3. CLI product layer

The CLI is no longer just a temporary debug surface.

It is currently the main product surface for:

- scan / inspect
- organize / rename
- duplicates and similar-review flows
- trip and cleanup workflows
- reporting and JSON output
- history and audit-oriented commands

### 4. Workflow composition layer

This layer sits on top of the CLI/Core contract and is now substantial enough to matter architecturally.

It includes:

- workflow presets
- saved workflow profiles
- profile validation and inventory
- profile bundles
- bundle compare / merge / extract / sync / run flows
- shell/form/launcher models for future UI consumption

This layer should remain **data- and contract-driven**, not GUI-driven.

### 5. GUI later

A GUI is still part of the long-term plan.

But it should consume:

- core planning/reporting models
- workflow/profile/bundle metadata
- shell/form/launcher models

It should not re-implement engine decisions.

## Current product shape

The repository is best understood as a shared core with several product-facing clusters:

1. **Inspect and date reasoning**
2. **Organize and rename**
3. **Duplicate review**
4. **Guided workflows**
5. **Workflow profiles and bundles**
6. **Shell/launcher/form models for later UI use**

## Architectural rules

### Core over presentation

No GUI or shell layer should decide:

- which date wins
- which duplicate candidate is kept
- whether a file is already compliant
- how collisions are resolved
- whether a workflow/profile is valid
- how a profile bundle is compared or merged

Those decisions belong in the core and workflow logic.

### Safety before convenience

Preview and reporting paths must exist before destructive execution becomes easy.

Examples:

- preview before apply
- visible skip reasons
- visible duplicate decisions
- visible workflow/profile validation problems
- auditable bundle/profile operations

### Additive contracts are preferred

The repository now has many tests that depend on:

- JSON field names
- text output fragments
- helper exports
- compatibility shims

That means architectural cleanup should prefer **additive improvement** over casual contract replacement.

### Windows-first is a real constraint

Path handling, quoting, file operations, and examples should continue to be checked with Windows behavior in mind.

### Workflow metadata is now part of the architecture

Workflow presets, profiles, inventories, bundles, shell forms, and launchers are no longer side notes. They are becoming a real composition layer over the core/CLI product.

That means they should be treated as first-class architectural pieces, not as throwaway convenience scripts.

## Immediate direction

Near-term architectural work should continue to improve:

- CLI/Core robustness
- reporting and journaling consistency
- profile/bundle usability and auditability
- clearer documentation and repository truthfulness

The goal is not to inflate the number of features. The goal is to make the existing surface more trustworthy and easier to operate.
