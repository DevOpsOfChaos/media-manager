# Next Steps

This file is the short product-direction checkpoint for the current active baseline.

## Current goal

The repository already has a cleaned core-first baseline with the CLI as the stable operational foundation.

The next goal is to introduce the GUI slowly and deliberately, without letting UI code duplicate business logic or bypass preview/apply safety contracts.

The GUI must stay a consumer of explicit core/application contracts: manifests, run artifacts, review workspaces, action models, journals, and undo-ready results.

## Product direction for the next phase

We will prioritize the following additions while the GUI layer is introduced in controlled, contract-driven steps:

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

5. **Application-layer contracts for GUI and CLI**
   - New features should expose service/application contracts before UI-specific behavior is added.
   - The CLI and GUI should both consume the same logic instead of becoming separate products.
   - GUI work should start with guarded review/workbench surfaces, not unrestricted destructive flows.

## Important rule

For the next implementation blocks, we prefer this order:

1. core/application logic
2. result and journal model
3. CLI flags and text/JSON output
4. GUI/workbench surface backed by the same contracts

## Immediate next design task

The immediate next task is to define a V1 for:

- associated files / media groups
- supported file types and matching rules
- leftover consolidation behavior
- required result fields
- required history / undo behavior

That definition should stay conservative, Windows-first, and safety-first.
