from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from media_manager.core.file_identity import files_have_identical_content

from .models import OrganizeDryRun, OrganizeExecutionEntry, OrganizeExecutionResult, OrganizeMemberExecution

if TYPE_CHECKING:
    from media_manager.core.progress_tracker import ProgressTracker


def _normalized_path_key(path: Path) -> str:
    return os.path.normcase(str(path))


def _build_member_specs(entry) -> list[tuple[Path, Path | None, str, bool]]:
    if entry.media_group is None:
        return [(entry.source_path, entry.target_path, "main", True)]

    role_by_path = {member.path: member.role for member in entry.media_group.members}
    ordered_paths = [member.path for member in entry.media_group.members]
    specs: list[tuple[Path, Path | None, str, bool]] = []
    for source_path in ordered_paths:
        specs.append(
            (
                source_path,
                entry.group_target_paths.get(source_path),
                role_by_path.get(source_path, "associated"),
                source_path == entry.source_path,
            )
        )
    return specs


def _member_results_for_nonexecuted_entry(entry, *, outcome: str, reason: str) -> list[OrganizeMemberExecution]:
    return [
        OrganizeMemberExecution(
            source_path=source_path,
            target_path=target_path,
            role=role,
            is_main_file=is_main_file,
            outcome=outcome,
            reason=reason,
        )
        for source_path, target_path, role, is_main_file in _build_member_specs(entry)
    ]


def _evaluate_apply_state(entry, *, conflict_policy: str = "conflict") -> tuple[str, str]:
    specs = _build_member_specs(entry)

    if any(target_path is None for _, target_path, _, _ in specs):
        return "error", "missing target path"

    same_path_count = sum(
        1
        for source_path, target_path, _, _ in specs
        if target_path is not None and _normalized_path_key(source_path) == _normalized_path_key(target_path)
    )
    if same_path_count == len(specs):
        return "skipped", "source already matches the planned target path at apply time"
    if same_path_count > 0:
        return "conflict", "one or more group members already match the planned target path at apply time"

    existing_count = 0
    identical_count = 0
    for source_path, target_path, _, _ in specs:
        if target_path is None or not target_path.exists():
            continue
        existing_count += 1
        if files_have_identical_content(source_path, target_path):
            identical_count += 1
        else:
            if conflict_policy == "skip":
                return "skipped", "target path already exists at apply time; skipped by conflict policy"
            return "conflict", "target path already exists at apply time"

    if existing_count:
        if identical_count == len(specs):
            return "skipped", "target already exists with identical file content at apply time"
        if conflict_policy == "skip":
            return "skipped", "one or more target paths already exist at apply time; skipped by conflict policy"
        return "conflict", "one or more target paths already exist at apply time"

    return "planned", "ready for organize execution"


def _rollback_group(performed: list[tuple[str, Path, Path]]) -> str | None:
    rollback_errors: list[str] = []
    for action, source_path, target_path in reversed(performed):
        try:
            if action == "moved":
                if target_path.exists() and not source_path.exists():
                    source_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(target_path), str(source_path))
            elif action == "copied":
                if target_path.exists():
                    target_path.unlink()
        except Exception as exc:  # pragma: no cover
            rollback_errors.append(str(exc))
    if rollback_errors:
        return "; ".join(rollback_errors)
    return None


def execute_organize_plan(plan: OrganizeDryRun, progress_callback=None,
                         progress: "ProgressTracker | None" = None,
                         checkpoint_path: Path | None = None,
                         resume: bool = False) -> OrganizeExecutionResult:
    """Execute an organize plan.

    Args:
        plan: The dry-run plan to execute.
        progress_callback: Legacy callback(current, total) — still supported.
        progress: New-style ProgressTracker for granular phase reporting.
        checkpoint_path: If set, write a checkpoint after each batch for resume support.
        resume: If True and checkpoint_path exists, skip already-processed entries.
    """
    from media_manager.core.progress_tracker import ProgressTracker  # local import avoids circular

    result = OrganizeExecutionResult(plan=plan)
    total = len(plan.entries)
    if total == 0:
        if progress:
            progress.done("No files to organize.")
        return result

    # ── Resume: determine start index from checkpoint ──
    start_index = 0
    checkpoint_data: dict | None = None
    if resume and checkpoint_path and checkpoint_path.exists():
        try:
            import json as _json
            checkpoint_data = _json.loads(checkpoint_path.read_text(encoding="utf-8"))
            start_index = int(checkpoint_data.get("last_processed_index", 0))
            if start_index >= total:
                start_index = total
        except Exception:
            start_index = 0

    # ── Phase: create directories ──
    if progress and start_index == 0:
        progress.enter_phase("creating_dirs", f"Creating {total:,} target folders...")
    dirs_created: set[Path] = set()
    for entry in plan.entries:
        if entry.status == "planned" and entry.target_path:
            parent = entry.target_path.parent
            if parent not in dirs_created:
                parent.mkdir(parents=True, exist_ok=True)
                dirs_created.add(parent)

    # ── Phase: move/copy files ──
    checkpoint_batch = 500  # save progress every 500 entries
    if progress:
        resume_note = f" (resuming from {start_index:,})" if start_index > 0 else ""
        progress.enter_phase("moving_files", f"Moving files... {start_index:,}/{total:,}{resume_note}")
    report_every = max(1, min(50, total // 200))  # throttle: every 50 files, or less for small plans
    done = 0
    for i, entry in enumerate(plan.entries):
        # Skip already-processed entries on resume
        if i < start_index:
            done += 1
            # Reconstruct a minimal skip result for result tracking
            if entry.status in ("skipped", "conflict", "error"):
                result.entries.append(
                    OrganizeExecutionEntry(
                        plan_entry=entry, outcome=entry.status, reason=entry.reason,
                        member_results=_member_results_for_nonexecuted_entry(entry, outcome=entry.status, reason=entry.reason),
                    )
                )
            else:
                # Already-processed entries: assume they were executed successfully
                outcome = "moved" if entry.operation_mode == "move" else "copied"
                result.entries.append(
                    OrganizeExecutionEntry(
                        plan_entry=entry, outcome=outcome, reason="resumed from checkpoint",
                        member_results=_member_results_for_nonexecuted_entry(entry, outcome=outcome, reason="resumed from checkpoint"),
                    )
                )
            if progress and done % report_every == 0:
                progress.tick_count(done, total, f"Resuming... {done:,}/{total:,}")
            continue

        done += 1

        # Report progress at finer granularity
        if progress and done % report_every == 0:
            progress.tick_count(done, total, f"Moving files... {done:,}/{total:,}")
        elif progress_callback and done % 200 == 0:
            progress_callback(done, total)

        if entry.status == "skipped":
            result.entries.append(
                OrganizeExecutionEntry(
                    plan_entry=entry, outcome="skipped", reason=entry.reason,
                    member_results=_member_results_for_nonexecuted_entry(entry, outcome="skipped", reason=entry.reason),
                )
            )
            continue
        if entry.status == "conflict":
            result.entries.append(
                OrganizeExecutionEntry(
                    plan_entry=entry, outcome="conflict", reason=entry.reason,
                    member_results=_member_results_for_nonexecuted_entry(entry, outcome="conflict", reason=entry.reason),
                )
            )
            continue
        if entry.status == "error":
            result.entries.append(
                OrganizeExecutionEntry(
                    plan_entry=entry, outcome="error", reason=entry.reason,
                    member_results=_member_results_for_nonexecuted_entry(entry, outcome="error", reason=entry.reason),
                )
            )
            continue

        current_status, current_reason = _evaluate_apply_state(entry, conflict_policy=plan.options.conflict_policy)
        if current_status != "planned":
            result.entries.append(
                OrganizeExecutionEntry(
                    plan_entry=entry, outcome=current_status, reason=current_reason,
                    member_results=_member_results_for_nonexecuted_entry(entry, outcome=current_status, reason=current_reason),
                )
            )
            continue

        performed: list[tuple[str, Path, Path]] = []
        member_results: list[OrganizeMemberExecution] = []
        specs = _build_member_specs(entry)
        try:
            for source_path, target_path, role, is_main_file in specs:
                if target_path is None:
                    raise RuntimeError("missing target path")
                # Directory already created in the pre-pass above
                if entry.operation_mode == "move":
                    shutil.move(str(source_path), str(target_path))
                    outcome = "moved"
                else:
                    shutil.copy2(str(source_path), str(target_path))
                    outcome = "copied"
                performed.append((outcome, source_path, target_path))
                member_results.append(
                    OrganizeMemberExecution(
                        source_path=source_path, target_path=target_path,
                        role=role, is_main_file=is_main_file,
                        outcome=outcome, reason="executed organize action",
                    )
                )
        except Exception as exc:  # pragma: no cover
            rollback_error = _rollback_group(performed)
            reason = f"organize group execution failed: {exc}"
            if rollback_error:
                reason = f"{reason} (rollback failed: {rollback_error})"
            result.entries.append(
                OrganizeExecutionEntry(
                    plan_entry=entry, outcome="error", reason=reason,
                    member_results=_member_results_for_nonexecuted_entry(entry, outcome="error", reason=reason),
                )
            )
            continue

        group_outcome = "moved" if entry.operation_mode == "move" else "copied"
        result.entries.append(
            OrganizeExecutionEntry(
                plan_entry=entry, outcome=group_outcome,
                reason="executed organize action", member_results=member_results,
            )
        )

        # ── Checkpoint: save progress every N entries ──
        if checkpoint_path and done % checkpoint_batch == 0:
            try:
                import json as _json
                checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
                checkpoint_path.write_text(
                    _json.dumps({
                        "last_processed_index": done,
                        "total": total,
                        "executed_count": result.executed_count,
                    }),
                    encoding="utf-8",
                )
            except Exception:
                pass

    # ── Final checkpoint + cleanup ──
    if checkpoint_path and checkpoint_path.exists():
        try:
            checkpoint_path.unlink()
        except Exception:
            pass

    if progress:
        progress.done(f"Done — {result.executed_count:,} files organized.")
    elif progress_callback:
        progress_callback(total, total)
    return result
