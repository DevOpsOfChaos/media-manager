from __future__ import annotations

import os

from .models import (
    RenameDryRun,
    RenameExecutionEntry,
    RenameExecutionResult,
    RenameMemberExecutionResult,
    RenameMemberTarget,
)


def _normalized_path_key(path) -> str:
    return os.path.normcase(str(path))


def _build_member_targets(item):
    if getattr(item, "member_targets", ()):
        return tuple(item.member_targets)
    if item.target_path is None:
        return ()
    return (RenameMemberTarget(source_path=item.source_path, target_path=item.target_path, role="main"),)


def execute_rename_dry_run(dry_run: RenameDryRun, *, apply: bool) -> RenameExecutionResult:
    result = RenameExecutionResult(apply_requested=apply)

    for item in dry_run.entries:
        result.processed_count += 1

        if item.status == "skipped":
            result.skipped_count += 1
            result.entries.append(
                RenameExecutionEntry(
                    source_path=item.source_path,
                    target_path=item.target_path,
                    status="skipped",
                    reason=item.reason,
                    action="skip",
                    plan_entry=item,
                )
            )
            continue
        if item.status == "conflict":
            result.conflict_count += 1
            result.entries.append(
                RenameExecutionEntry(
                    source_path=item.source_path,
                    target_path=item.target_path,
                    status="conflict",
                    reason=item.reason,
                    action="conflict",
                    plan_entry=item,
                )
            )
            continue
        if item.status == "error" or item.target_path is None:
            result.error_count += 1
            result.entries.append(
                RenameExecutionEntry(
                    source_path=item.source_path,
                    target_path=item.target_path,
                    status="error",
                    reason=item.reason,
                    action="error",
                    plan_entry=item,
                )
            )
            continue

        member_targets = _build_member_targets(item)

        if not apply:
            result.preview_count += 1
            member_results = tuple(
                RenameMemberExecutionResult(
                    source_path=member.source_path,
                    target_path=member.target_path,
                    status="planned",
                    reason=item.reason,
                    action="preview-rename",
                    role=member.role,
                )
                for member in member_targets
            )
            result.entries.append(
                RenameExecutionEntry(
                    source_path=item.source_path,
                    target_path=item.target_path,
                    status="planned",
                    reason=item.reason,
                    action="preview-rename",
                    plan_entry=item,
                    member_results=member_results,
                )
            )
            continue

        source_match = all(
            _normalized_path_key(member.source_path) == _normalized_path_key(member.target_path)
            for member in member_targets
        )
        if source_match:
            result.skipped_count += 1
            result.entries.append(
                RenameExecutionEntry(
                    source_path=item.source_path,
                    target_path=item.target_path,
                    status="skipped",
                    reason="source file already matches the planned rename target at apply time",
                    action="skip",
                    plan_entry=item,
                )
            )
            continue

        missing_member = next((member for member in member_targets if not member.source_path.exists()), None)
        if missing_member is not None:
            result.error_count += 1
            result.entries.append(
                RenameExecutionEntry(
                    source_path=item.source_path,
                    target_path=item.target_path,
                    status="error",
                    reason="source file no longer exists at apply time",
                    action="error",
                    plan_entry=item,
                )
            )
            continue

        conflicting_member = next(
            (
                member
                for member in member_targets
                if _normalized_path_key(member.source_path) != _normalized_path_key(member.target_path)
                and member.target_path.exists()
            ),
            None,
        )
        if conflicting_member is not None:
            if dry_run.options.conflict_policy == "skip":
                result.skipped_count += 1
                result.entries.append(
                    RenameExecutionEntry(
                        source_path=item.source_path,
                        target_path=item.target_path,
                        status="skipped",
                        reason="target file name already exists at apply time; skipped by conflict policy",
                        action="skip",
                        plan_entry=item,
                    )
                )
            else:
                result.conflict_count += 1
                result.entries.append(
                    RenameExecutionEntry(
                        source_path=item.source_path,
                        target_path=item.target_path,
                        status="conflict",
                        reason="target file name already exists at apply time",
                        action="conflict",
                        plan_entry=item,
                    )
                )
            continue

        completed = []
        member_results = []
        try:
            for member in member_targets:
                member.source_path.rename(member.target_path)
                completed.append((member.target_path, member.source_path))
                member_results.append(
                    RenameMemberExecutionResult(
                        source_path=member.source_path,
                        target_path=member.target_path,
                        status="renamed",
                        reason="rename applied successfully",
                        action="renamed",
                        role=member.role,
                    )
                )
        except OSError as exc:
            for done_target, done_source in reversed(completed):
                try:
                    if done_target.exists() and not done_source.exists():
                        done_target.rename(done_source)
                except OSError:
                    pass
            result.error_count += 1
            result.entries.append(
                RenameExecutionEntry(
                    source_path=item.source_path,
                    target_path=item.target_path,
                    status="error",
                    reason=str(exc),
                    action="error",
                    plan_entry=item,
                )
            )
            continue

        result.renamed_count += 1
        result.entries.append(
            RenameExecutionEntry(
                source_path=item.source_path,
                target_path=item.target_path,
                status="renamed",
                reason="rename applied successfully",
                action="renamed",
                plan_entry=item,
                member_results=tuple(member_results),
            )
        )

    return result
