from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .cleanup_plan import ExactCleanupDryRun


@dataclass(slots=True)
class ExecutionPreviewRow:
    row_type: str
    status: str
    group_id: str
    operation_mode: str
    source_path: Path
    survivor_path: Path | None
    target_path: Path | None
    file_size: int
    reason: str


@dataclass(slots=True)
class DuplicateExecutionPreview:
    ready: bool
    rows: list[ExecutionPreviewRow] = field(default_factory=list)

    @property
    def executable_count(self) -> int:
        return sum(1 for row in self.rows if row.status == "executable")

    @property
    def deferred_count(self) -> int:
        return sum(1 for row in self.rows if row.status == "deferred")

    @property
    def blocked_count(self) -> int:
        return sum(1 for row in self.rows if row.status == "blocked")

    @property
    def delete_count(self) -> int:
        return sum(1 for row in self.rows if row.row_type == "filesystem_delete")


def build_duplicate_execution_preview(dry_run: ExactCleanupDryRun) -> DuplicateExecutionPreview:
    """
    Convert the exact-duplicate dry run into an execution-oriented preview model.

    This remains intentionally limited to the exact-duplicate path.
    It does not execute anything and it does not yet model sorting / rename file-system work.
    """
    preview = DuplicateExecutionPreview(ready=dry_run.ready)

    for action in dry_run.planned_actions:
        if action.action_type == "delete":
            preview.rows.append(
                ExecutionPreviewRow(
                    row_type="filesystem_delete",
                    status="executable",
                    group_id=action.group_id,
                    operation_mode=action.operation_mode,
                    source_path=action.source_path,
                    survivor_path=action.survivor_path,
                    target_path=action.target_path,
                    file_size=action.file_size,
                    reason=action.reason,
                )
            )
            continue

        preview.rows.append(
            ExecutionPreviewRow(
                row_type="pipeline_exclusion",
                status="deferred",
                group_id=action.group_id,
                operation_mode=action.operation_mode,
                source_path=action.source_path,
                survivor_path=action.survivor_path,
                target_path=action.target_path,
                file_size=action.file_size,
                reason=action.reason,
            )
        )

    for action in dry_run.blocked_actions:
        preview.rows.append(
            ExecutionPreviewRow(
                row_type="blocked",
                status="blocked",
                group_id=action.group_id,
                operation_mode=action.operation_mode,
                source_path=action.source_path,
                survivor_path=action.survivor_path,
                target_path=action.target_path,
                file_size=action.file_size,
                reason=action.reason,
            )
        )

    return preview
