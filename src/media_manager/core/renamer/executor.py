
from __future__ import annotations

from .models import RenameDryRun, RenameExecutionEntry, RenameExecutionResult


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
                )
            )
            continue

        if not apply:
            result.preview_count += 1
            result.entries.append(
                RenameExecutionEntry(
                    source_path=item.source_path,
                    target_path=item.target_path,
                    status="planned",
                    reason=item.reason,
                    action="preview-rename",
                )
            )
            continue

        if not item.source_path.exists():
            result.error_count += 1
            result.entries.append(
                RenameExecutionEntry(
                    source_path=item.source_path,
                    target_path=item.target_path,
                    status="error",
                    reason="source file no longer exists at apply time",
                    action="error",
                )
            )
            continue

        if item.target_path.exists():
            result.conflict_count += 1
            result.entries.append(
                RenameExecutionEntry(
                    source_path=item.source_path,
                    target_path=item.target_path,
                    status="conflict",
                    reason="target file name already exists at apply time",
                    action="conflict",
                )
            )
            continue

        item.source_path.rename(item.target_path)
        result.renamed_count += 1
        result.entries.append(
            RenameExecutionEntry(
                source_path=item.source_path,
                target_path=item.target_path,
                status="renamed",
                reason="rename applied successfully",
                action="renamed",
            )
        )

    return result
