from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from send2trash import send2trash

from .execution_plan import DuplicateExecutionPreview
from .execution_safety import find_associated_sibling_paths


@dataclass(slots=True)
class ExecutionRunEntry:
    row_type: str
    status: str
    source_path: Path
    survivor_path: Path | None
    target_path: Path | None
    outcome: str
    reason: str


@dataclass(slots=True)
class DuplicateExecutionRunResult:
    processed_rows: int = 0
    executable_rows: int = 0
    executed_rows: int = 0
    deferred_rows: int = 0
    blocked_rows: int = 0
    error_rows: int = 0
    entries: list[ExecutionRunEntry] = field(default_factory=list)

    @property
    def previewed_rows(self) -> int:
        return sum(1 for entry in self.entries if entry.outcome == "preview-delete")

    @property
    def deleted_rows(self) -> int:
        return sum(1 for entry in self.entries if entry.outcome == "deleted")

    @property
    def blocked_associated_rows(self) -> int:
        return sum(1 for entry in self.entries if entry.reason == "associated_files_present")

    @property
    def blocked_missing_survivor_rows(self) -> int:
        return sum(1 for entry in self.entries if entry.reason == "survivor_missing")


def run_duplicate_execution_preview(
    preview: DuplicateExecutionPreview,
    *,
    apply: bool = False,
) -> DuplicateExecutionRunResult:
    """
    Execute or preview only the currently executable duplicate rows.

    Current scope intentionally stays narrow:
    - `filesystem_delete` rows are previewed or sent to trash
    - `pipeline_exclusion` rows stay deferred because later copy/move pipeline integration does not exist yet
    - `blocked` rows stay blocked
    """
    result = DuplicateExecutionRunResult()

    for row in preview.rows:
        result.processed_rows += 1

        if row.status == "blocked" or row.row_type == "blocked":
            result.blocked_rows += 1
            result.entries.append(
                ExecutionRunEntry(
                    row_type=row.row_type,
                    status=row.status,
                    source_path=row.source_path,
                    survivor_path=row.survivor_path,
                    target_path=row.target_path,
                    outcome="blocked",
                    reason=row.reason,
                )
            )
            continue

        if row.row_type == "pipeline_exclusion" or row.status == "deferred":
            result.deferred_rows += 1
            result.entries.append(
                ExecutionRunEntry(
                    row_type=row.row_type,
                    status=row.status,
                    source_path=row.source_path,
                    survivor_path=row.survivor_path,
                    target_path=row.target_path,
                    outcome="deferred",
                    reason=row.reason,
                )
            )
            continue

        if row.row_type != "filesystem_delete" or row.status != "executable":
            result.error_rows += 1
            result.entries.append(
                ExecutionRunEntry(
                    row_type=row.row_type,
                    status=row.status,
                    source_path=row.source_path,
                    survivor_path=row.survivor_path,
                    target_path=row.target_path,
                    outcome="error",
                    reason=f"unsupported execution row: {row.row_type}/{row.status}",
                )
            )
            continue

        result.executable_rows += 1

        if not row.source_path.exists():
            result.error_rows += 1
            result.entries.append(
                ExecutionRunEntry(
                    row_type=row.row_type,
                    status=row.status,
                    source_path=row.source_path,
                    survivor_path=row.survivor_path,
                    target_path=row.target_path,
                    outcome="error",
                    reason="source_missing",
                )
            )
            continue

        if row.survivor_path is None or not row.survivor_path.exists():
            result.blocked_rows += 1
            result.entries.append(
                ExecutionRunEntry(
                    row_type="blocked_missing_survivor",
                    status="blocked",
                    source_path=row.source_path,
                    survivor_path=row.survivor_path,
                    target_path=row.target_path,
                    outcome="blocked",
                    reason="survivor_missing",
                )
            )
            continue

        if find_associated_sibling_paths(row.source_path):
            result.blocked_rows += 1
            result.entries.append(
                ExecutionRunEntry(
                    row_type="blocked_associated_files",
                    status="blocked",
                    source_path=row.source_path,
                    survivor_path=row.survivor_path,
                    target_path=row.target_path,
                    outcome="blocked",
                    reason="associated_files_present",
                )
            )
            continue

        if not apply:
            result.executed_rows += 1
            result.entries.append(
                ExecutionRunEntry(
                    row_type=row.row_type,
                    status=row.status,
                    source_path=row.source_path,
                    survivor_path=row.survivor_path,
                    target_path=row.target_path,
                    outcome="preview-delete",
                    reason=row.reason,
                )
            )
            continue

        try:
            send2trash(str(row.source_path))
        except Exception as exc:  # pragma: no cover - runtime safeguard
            result.error_rows += 1
            result.entries.append(
                ExecutionRunEntry(
                    row_type=row.row_type,
                    status=row.status,
                    source_path=row.source_path,
                    survivor_path=row.survivor_path,
                    target_path=row.target_path,
                    outcome="error",
                    reason=str(exc),
                )
            )
            continue

        result.executed_rows += 1
        result.entries.append(
            ExecutionRunEntry(
                row_type=row.row_type,
                status=row.status,
                source_path=row.source_path,
                survivor_path=row.survivor_path,
                target_path=row.target_path,
                outcome="deleted",
                reason=row.reason,
            )
        )

    return result
