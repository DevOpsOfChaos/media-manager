from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from send2trash import send2trash

from .duplicates import files_are_identical
from .execution_plan import DuplicateExecutionPreview, ExecutionPreviewRow
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
    - delete rows are revalidated against the current file system before preview/apply
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

        if row.source_path.stat().st_size != row.file_size:
            result.blocked_rows += 1
            result.entries.append(
                ExecutionRunEntry(
                    row_type="blocked_stale_source",
                    status="blocked",
                    source_path=row.source_path,
                    survivor_path=row.survivor_path,
                    target_path=row.target_path,
                    outcome="blocked",
                    reason="source_size_changed_since_scan",
                )
            )
            continue

        if row.survivor_path is None:
            result.error_rows += 1
            result.entries.append(
                ExecutionRunEntry(
                    row_type="missing_survivor_reference",
                    status="error",
                    source_path=row.source_path,
                    survivor_path=row.survivor_path,
                    target_path=row.target_path,
                    outcome="error",
                    reason="survivor_missing_from_execution_row",
                )
            )
            continue

        if not row.survivor_path.exists():
            result.blocked_rows += 1
            result.entries.append(
                ExecutionRunEntry(
                    row_type="blocked_missing_survivor",
                    status="blocked",
                    source_path=row.source_path,
                    survivor_path=row.survivor_path,
                    target_path=row.target_path,
                    outcome="blocked",
                    reason="survivor_missing_on_disk",
                )
            )
            continue

        if not files_are_identical(row.source_path, row.survivor_path):
            result.blocked_rows += 1
            result.entries.append(
                ExecutionRunEntry(
                    row_type="blocked_stale_duplicate",
                    status="blocked",
                    source_path=row.source_path,
                    survivor_path=row.survivor_path,
                    target_path=row.target_path,
                    outcome="blocked",
                    reason="source_no_longer_matches_survivor",
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
                    outcome="preview-trash",
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
                outcome="trashed",
                reason=row.reason,
            )
        )

    return result
