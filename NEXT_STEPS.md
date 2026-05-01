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
   - The current GUI-facing contract inventory is available through `media-manager app-services contracts --json`. The GUI surface binding gate is available through `media-manager app-services contract-bindings --json`; new GUI work should keep both payloads green before adding UI-specific behavior.
   - The Review Workbench page is now a real headless runtime target via `media-manager app-services review-workbench`, `media-manager app-services review-workbench-widget-bindings`, `media-manager app-services review-workbench-widget-skeleton`, `media-manager app-services review-workbench-interactions`, `media-manager app-services review-workbench-callback-mounts`, `media-manager app-services review-workbench-apply-preview`, `media-manager app-services review-workbench-confirmation-dialog`, `media-manager app-services review-workbench-apply-executor-contract`, `media-manager app-services review-workbench-apply-handoff-panel`, `media-manager app-services review-workbench-stateful-rebuild`, `media-manager app-services review-workbench-stateful-callbacks`, and `media-manager app-services desktop-runtime --active-page review-workbench`. The Qt desktop renderer now has a PySide6-lazy Review Workbench builder plus non-executing interaction intents and concrete callback mounts for filters, lane selection, row activation, refresh, reset, detail actions, and route requests. The visible confirmation/executor handoff panel is now wired as a display-only contract. The stateful rebuild loop now applies filter, selection, sort, paging, reset, and refresh intents and returns a replacement Review Workbench page-state bundle without enabling execution. Lazy Qt callbacks can now call that loop through a `stateful_rebuild_handler`, so the next GUI step is controlled in-place re-rendering of the Review Workbench page from returned `next_page_state`, not a parallel GUI-only state store or execution path.

## Important rule

For the next implementation blocks, we prefer this order:

1. core/application logic
2. result and journal model
3. CLI flags and text/JSON output
4. GUI/workbench surface bound through `contract-bindings` and backed by the same contracts
5. real Qt widgets consume the Review Workbench widget skeleton, interaction plan, callback mounts, stateful callback bridge, apply-preview command-plan contract, confirmation dialog, executor contract, and handoff panel without bypassing route intents or command plans

## Immediate next design task

The immediate next task is to define a V1 for:

- associated files / media groups
- supported file types and matching rules
- leftover consolidation behavior
- required result fields
- required history / undo behavior

That definition should stay conservative, Windows-first, and safety-first.
