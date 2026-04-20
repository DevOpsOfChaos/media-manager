# Next Steps

This file is the short product-direction checkpoint for the current active baseline.

## Current goal

The repository already has a cleaned CLI-first / core-first baseline.

The next goal is **not** to expand a GUI yet.

The next goal is to make the CLI/core foundation strong enough that a future GUI can be built on top of it without duplicating business logic.

## Product direction for the next phase

We will prioritize the following additions before starting a new GUI layer:

1. **Associated files / media groups**
   - Treat a main media file together with known related files as one operational unit.
   - Examples: XMP sidecars, AAE files, RAW+JPEG pairs, photo+video pairs where the mapping is clear.
   - This must work in preview, apply, journaling, history, and undo.

2. **Source leftover consolidation**
   - Optional and disabled by default.
   - After a successful apply-run, remaining files in a source can be moved into a single leftover folder per source.
   - After that, empty source subdirectories can be removed.
   - This must be journaled and undoable.

3. **Conflict policy as an explicit product feature**
   - Conflict handling must become a defined part of the product instead of scattered command behavior.
   - Policies should stay explainable and previewable.

4. **Review / manual-check output paths**
   - Distinguish between normal leftovers and files that require manual review.

5. **Application-layer preparation for a future GUI**
   - New features should be added in a way that later supports a service/application layer.
   - The CLI should be a consumer of the logic, not the only place where the logic exists.

## Important rule

For the next implementation blocks, we prefer this order:

1. core/application logic
2. result and journal model
3. CLI flags and text/JSON output
4. GUI later

## Immediate next design task

The immediate next task is to define a V1 for:

- associated files / media groups
- supported file types and matching rules
- leftover consolidation behavior
- required result fields
- required history / undo behavior

That definition should stay conservative, Windows-first, and safety-first.
