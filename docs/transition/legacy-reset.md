# Legacy Reset Note

## Why this document still exists

This repository did go through a real reset.

That historical note is still useful, but it should now be read with one important update in mind:

The project is **not only a reset skeleton anymore**.

It has an active CLI/Core direction with growing workflow, profile, and bundle layers on top.

## What the reset changed

The repository kept:

- its name
- its history
- useful pieces of older work

But the active product direction changed to a **core-first, CLI-first rebuild**.

That shift remains valid.

## What still counts as legacy

A file, subsystem, or direction should still be treated as legacy when it:

- couples business logic tightly to GUI state
- assumes the GUI is the product driver before the engine is stable
- hides weak planning or date logic behind interface work
- is useful as reference material but not as the right base for future changes

## What now counts as active direction

The active direction now includes more than the earliest reset docs used to admit.

It is centered on:

1. scan and inspect
2. date resolution and reporting
3. organize and rename planning/execution
4. duplicates and review flows
5. state/history/journaling layers
6. guided workflows
7. workflow presets, profiles, and bundles
8. shell/form/launcher models for later UI use
9. GUI later

## How to treat old code now

Old code may still be:

- mined for utilities
- mined for tests
- mined for path handling or parsing ideas
- kept temporarily while current layers continue to mature

But old code should still **not** define the architecture by inertia.

## Practical policy

- keep docs honest about what is current
- keep legacy-heavy areas clearly marked when needed
- continue preferring core/CLI/workflow reliability over GUI expansion
- avoid pretending every older subsystem is equally current
- preserve useful history without letting it blur product direction

## Short version

The repository was not abandoned.

It was reset to become more honest.

And by now, that reset has already grown into a meaningful CLI/Core product layer that the documentation should reflect clearly.
