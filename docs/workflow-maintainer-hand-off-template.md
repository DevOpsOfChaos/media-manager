# Workflow maintainer hand-off template

Use this as a compact template when handing work from one chat/session/block to the next.

The goal is to preserve:

- the real current repo truth
- the exact scope of the last green block
- the most important compatibility traps
- the right next-step options

---

## Repo and branch truth

- Repository: `DevOpsOfChaos/media-manager`
- Source of truth: current `main`
- Platform priority: Windows first
- Product priority: core/CLI first
- Output language: English first

## Last confirmed green block

Describe the last block that is definitely green and, if known, pushed.

Example:

- workflow history date filters in CLI
- history latest-by-command core helpers
- docs navigation refresh

Be explicit if something was prepared but not confirmed as pushed.

## Files changed in the last confirmed block

List the exact files, not only the feature title.

Example:

- `src/media_manager/core/state/history.py`
- `src/media_manager/core/state/__init__.py`
- `tests/test_core_history_latest_by_command_v1.py`

## Broad checks that were actually run

List the checks that really ran green.

Example:

- `pytest -q tests/test_core_history_latest_by_command_v1.py`
- `pytest -q tests/test_core_history_summary_by_command_v1.py`
- `pytest -q`

This matters because “locally plausible” is not the same thing as “actually checked”.

## Compatibility-sensitive surfaces touched recently

Mark the fragile areas explicitly.

Common examples:

- `src/media_manager/core/state/__init__.py` re-exports
- workflow history JSON shape
- workflow bundle dataclass constructor compatibility
- Windows path normalization in filters
- package-root `src/media_manager/__init__.py`

## Known traps to avoid next

Write these bluntly.

Examples:

- do not change top-level JSON fields in `workflow last` without checking full compatibility tests
- do not overwrite `core.state.__init__.py` partially; keep cumulative exports intact
- do not return dicts where tests expect lists of model objects
- do not switch string path fields back to `Path` without checking the regression surface

## Next good large blocks

List 2–4 realistic next blocks so the next session can continue without losing time.

Examples:

- additive workflow history CLI command on top of existing core helpers
- cleanup workflow hardening and reporting polish
- bundle/run-dir audit polish
- docs/maintainer consolidation

## Recommended first action in the next session

Keep this concrete.

Examples:

- verify current `core.state.__init__.py` against the last known green export surface
- continue with additive docs-only block if the tree is fragile
- add one new workflow history command without touching `history`/`last` contracts

## Final note style

A good hand-off is:

- compact
- explicit about what is truly green
- honest about uncertainty
- focused on the exact break risks

A bad hand-off is:

- based on memory instead of the current repo
- vague about whether something was fully tested
- silent about compatibility-sensitive files
