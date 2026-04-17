# Architecture Notes

## Design goal

Build a trustworthy media-management core first.

That core must remain independent from the CLI and from any later GUI so the project can evolve without rewriting the actual media logic every time the interface changes.

## Architectural reset

Earlier repository phases explored desktop-first directions too early.

The current reset changes the order of work:

1. core media logic
2. CLI workflows
3. state and idempotent processing
4. duplicate handling
5. guided workflows
6. GUI later

This is not cosmetic repositioning. It is a structural correction.

## Target layers

### 1. Core domain

This layer is responsible for:

- discovering media files
- reading metadata through ExifTool
- resolving the best available capture date
- planning target paths
- planning rename results
- detecting duplicates
- deciding what is already compliant and should be skipped

This layer must not know anything about widgets, windows, or presentation state.

### 2. State layer

This layer is responsible for:

- run history
- file fingerprints
- planned versus executed actions
- idempotent skip decisions
- undo / journal support later

A lightweight SQLite-backed implementation is the intended direction.

### 3. CLI layer

The CLI is the first real product surface.

Its responsibilities are:

- collecting user options
- launching scans, inspections, plans, and apply steps
- rendering safe human-readable output
- exporting machine-readable reports later

The CLI should expose the real engine clearly enough that the later GUI becomes a thinner interface, not a second system.

### 4. GUI layer

A GUI is still part of the long-term plan.

But it comes after the core and CLI are stable enough that the interface is wrapping good behavior instead of compensating for missing foundations.

## Target product modules

The intended product shape is best understood as these modules built on one shared core:

1. **Scan / Inspect**
2. **Organize**
3. **Rename**
4. **Duplicates**
5. **Workflows**

## Target package direction

```text
src/media_manager/
  cli.py
  config.py
  scanner/
  metadata/
  date_resolver/
  organizer/
  renamer/
  state/
  reporting/
  workflows/
  duplicates/
  utils/
```

## Key technical rules

### Core/UI separation

No GUI code should decide:

- which metadata date wins
- whether a file is already compliant
- how duplicates are grouped
- how collisions are resolved
- whether a file should be skipped or processed

Those decisions belong in the core.

### Safety first

Preview modes and reviewable plans should come before destructive actions.

Deleting or overwriting media without a visible review path is not acceptable.

### Idempotence

The project must move beyond one-shot scripting behavior.

Important examples:

- files already in the correct target location should be skipped
- files already matching the naming template should not be renamed again
- prior processing decisions should be reusable where safe
- rerunning the same operation should not create avoidable churn

### Date resolution must be explainable

The project cannot rely on a flat metadata-date shortcut forever.

It needs a real date-resolution system that can report:

- chosen date
- source tag or fallback source
- confidence level
- timezone status
- reasoning

### Legacy code is reference, not authority

Older desktop-oriented code may still hold useful snippets or tests.

But the new architecture must not be forced to preserve weak abstractions just because they already exist in the repository.

## Non-goals during the reset

- pretending the legacy structure is already correct
- building a new GUI before the engine stabilizes
- hiding architectural uncertainty behind polished screenshots
- introducing fake complexity without product value

## Immediate implementation direction

The first rebuild milestone should focus on:

1. file discovery
2. metadata inspection
3. date-resolution baseline
4. dry-run organization planning
5. rename-template planning
6. reporting baseline

Only after that foundation is solid should the project expand into duplicate review, guided workflows, and later a modern GUI.
