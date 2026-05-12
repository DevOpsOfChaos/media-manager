# Next Steps

This file is the short product-direction checkpoint for the current active baseline.

## Current goal

The repository has a cleaned core-first baseline with the CLI as the stable operational foundation. The old PySide6 desktop GUI has been removed.

The new desktop frontend under `./desktop` (Tauri + React + TypeScript + shadcn/ui) is a **fresh redesign** — not a visual or structural port of the old PySide6 GUI. The old PySide6 files are historical reference only. Remaining `core/gui_qt_*` modules serve as functional inventory and headless contract references, not design direction. The new frontend consumes explicit core/application contracts: manifests, run artifacts, review workspaces, action models, journals, and undo-ready results. See [docs/ui-migration.md](docs/ui-migration.md) for the full design boundary.

## Desktop implementation status (2026-05-12)

**Finished:**
- Tauri + React + shadcn/ui scaffold under `./desktop`
- Settings bridge: read/write/reset via `bridge_settings.py`
- Runtime Diagnostics bridge via `bridge_diagnostics.py`
- Run History bridge: list/get via `bridge_history.py`
- Dashboard: composed real summary from diagnostics, settings, history (with Refresh)
- Organize Preview bridge: `bridge_organize_preview.py` — calls `build_organize_dry_run()` only, **never modifies files**
- Organize frontend: preview-only UI (source, target, pattern, options, results table, outcome report)
- History: search/filter, Refresh
- Settings: collapsible Runtime Diagnostics
- Quick navigation cards on Dashboard

**Preview-only guarantees:**
- `bridge_organize_preview.py` calls `build_organize_dry_run()` and explicitly marks results as `kind: "preview"`, `dry_run: true`
- The bridge does not import or call `execute_organize_plan()`
- The desktop UI shows "Preview only. No files are modified." and has no Apply button
- `organize_apply` Tauri command remains stubbed (returns error)

**Not yet implemented:**
- Organize Apply / execution
- Duplicates scan
- People scan
- Undo preview/apply
- Progress streaming
- Review Workbench

## Product direction for the next phase

We will prioritize the following additions while the new Tauri + React desktop frontend is introduced under `./desktop`:

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
   - The Review Workbench page is a headless runtime target via `media-manager app-services review-workbench` and related subcommands. The old PySide6 desktop GUI has been removed. The new desktop frontend lives under `./desktop` (Tauri + React + TypeScript + shadcn/ui). Headless contract/blueprint modules in `core/gui_qt_*` remain as reference designs for the new UI.

## Important rule

For the next implementation blocks, we prefer this order:

1. core/application logic
2. result and journal model
3. CLI flags and text/JSON output
4. GUI/workbench surface bound through `contract-bindings` and backed by the same contracts
5. the new Tauri + React desktop frontend consumes the Review Workbench contracts, widget skeletons, interaction plans, and apply-preview contracts through a stable API boundary

## Immediate next design task

The immediate next task is to define a V1 for:

- associated files / media groups
- supported file types and matching rules
- leftover consolidation behavior
- required result fields
- required history / undo behavior

That definition should stay conservative, Windows-first, and safety-first.
