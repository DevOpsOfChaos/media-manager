# Desktop Review Safety Requirements

This document defines the safety infrastructure that must exist before any destructive action (delete, move, rename, apply) can be implemented in the Tauri desktop app.

## Current Status (2026-05-14)

- Review Workbench is **read-only**.
- Decisions are **not persisted** to disk.
- Draft decisions exist **in memory only** and are lost on page navigation.
- **All apply/execute Tauri commands** return "not yet implemented".
- No files are deleted, moved, renamed, or modified by any desktop UI flow.

## Backend Decision Infrastructure (exists, not wired to desktop)

The Python backend already has a mature decision/apply pipeline gated behind CLI flags:

### Decision formats
| Type | Data Structure | File |
|------|---------------|------|
| Exact duplicates | `{group_id: keep_path}` | `core/duplicate_decisions.py` |
| Similar images | `{group_id: {path: "keep\|remove\|skip"}}` | `core/similar_decisions.py` |

### Journal format
```json
{
  "schema_version": 1,
  "journal_type": "execution_journal",
  "entries": [{
    "reversible": true,
    "undo_action": "move_back|rename_back|delete_target",
    "undo_from_path": "...",
    "undo_to_path": "...",
    "outcome": "deleted|moved|renamed|error",
    "reason": "..."
  }]
}
```

### Apply pipeline (CLI only, gated by --apply --yes)
```
Scan → Decision file → Import decisions → Build workflow bundle →
Execution preview (read-only) → Apply (destructive) → Journal written → Undo available
```

## Required Before Any Destructive Desktop Action

### 1. Decision persistence
- [ ] Decision file format agreed and documented
- [ ] Write path secured (user-visible directory, not hidden)
- [ ] Load/import path verified (signature check against current scan)
- [ ] Conflict detection (decisions refer to files that still exist)

### 2. Dry-run action model
- [ ] `build_action_model_from_report()` produces inspect/review/apply actions
- [ ] Apply actions are disabled by default
- [ ] Apply actions show risk level (destructive/high/medium)
- [ ] Apply actions require typed confirmation

### 3. Journal write
- [ ] Every destructive run writes an execution journal
- [ ] Journal includes undo_from_path and undo_to_path for every entry
- [ ] Journal is written before any file modification
- [ ] Journal schema versioned

### 4. Undo plan
- [ ] Undo plan derived from journal before execution
- [ ] Undo preview shows what would be restored
- [ ] Undo requires explicit confirmation
- [ ] Undo not available if journal is missing or incomplete

### 5. Preflight checks
- [ ] Source files still exist at recorded paths
- [ ] Target paths do not overwrite existing files (unless explicitly skipped)
- [ ] Associated sibling files detected and protected (RAW+JPEG pairs)
- [ ] No file is selected for deletion that has associated siblings
- [ ] Disk space check (enough space for copy/move operations)

### 6. User confirmation
- [ ] Summary of planned actions displayed
- [ ] Count of files to be affected
- [ ] Estimated reclaimable space (for deletions)
- [ ] Typed confirmation phrase required (not just a checkbox)
- [ ] No "select all" or "apply to all" without per-group review

### 7. Test coverage
- [ ] All destructive paths tested with tmp_path fixtures
- [ ] No real media files used in tests
- [ ] Undo tested end-to-end (apply → undo → verify original state)
- [ ] Guardrail tests (max_images, max_pairs) continue to pass
- [ ] Decision import edge cases tested (missing files, changed groups)

### 8. Tauri WebView smoke
- [ ] Apply workflow smoke-tested in real Tauri window with temp files
- [ ] Undo workflow smoke-tested
- [ ] Error states (missing files, permission denied) tested

## Safety Principles

1. **Preview first**. Every destructive operation must have a read-only preview that shows exactly what will happen.

2. **No hidden writes**. All file modifications must be explicitly requested by the user and confirmed through a typed-phrase dialog.

3. **No auto-delete**. The app must never automatically select files for deletion. Every removal decision must be made explicitly by the user.

4. **Neutral language**. UI must never use "recommended delete", "safe to remove", or similar phrasing. Use "candidate", "group member", "future decision".

5. **No destructive defaults**. Every destructive command must be opt-in. No checkbox pre-checked for deletion.

6. **Every destructive run is journaled**. Journal must be written before the first file modification. Undo must be available for every journaled run.

7. **Associated files protected**. Files with the same stem but different extensions (RAW+JPEG, photo+video pairs) must be treated as atomic units. Deleting one without the other requires explicit confirmation.

## Review Workbench Model (desktop, in-memory only)

The desktop Review Workbench defines a frontend-only model (`desktop/src/types/review.ts`) with:

- `ReviewSourceKind`: "exact_duplicates" | "similar_images"
- `ReviewGroup`: a cluster of candidate files
- `ReviewCandidate`: a single file with draft decision, role, safety state
- `ReviewDecisionDraft`: "undecided" | "keep_reference" | "remove_later" | "ignore"
- `ReviewSafetyState`: always `safe_to_remove: false` in preview

**All values are in-memory only.** No persistence. No apply. No journal write.
