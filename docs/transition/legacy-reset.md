# Legacy Reset Note

## Why this document exists

This repository had already grown beyond the original sorting script, but it also drifted into desktop- and GUI-heavy directions before the core architecture was strong enough.

This document marks the point where the repository is intentionally reset.

## What the reset means

The repository history is kept.

The repository name is kept.

But the active product direction changes to a **core-first rebuild**.

That means current and older implementation areas are no longer all treated as equally current.

## What counts as legacy

A file, subsystem, or direction should be treated as legacy when it:

- couples business logic too tightly to GUI state
- assumes the UI is the main product driver before the engine is stable
- hides weak date-resolution or planning logic behind interface work
- is useful as reference material but not as the right base for future work

## What counts as active direction

The active direction is now centered on:

1. scan
2. inspect
3. date resolution
4. organize planning
5. rename planning
6. state and idempotence
7. duplicates
8. workflows
9. GUI later

## How to treat old code during the reset

Old code may still be:

- reused in small pieces
- mined for tests
- mined for path handling or utility functions
- kept temporarily while the new structure is built

But old code should not dictate the new architecture just because it already exists.

## Practical migration policy

- keep useful documentation where it still matches the new direction
- rewrite misleading top-level documentation first
- move or mark legacy-heavy areas clearly
- prefer building new core modules over stretching old abstractions further
- do not pretend the legacy implementation is already the target product

## Short version

The repository is not being abandoned.

It is being made honest.
