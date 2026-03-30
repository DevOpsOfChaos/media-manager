from __future__ import annotations

from pathlib import Path

from .execution_plan import DuplicateExecutionPreview, ExecutionPreviewRow


def find_associated_sibling_paths(path: str | Path) -> list[Path]:
    file_path = Path(path)
    try:
        candidates = [candidate for candidate in file_path.parent.iterdir() if candidate.stem.casefold() == file_path.stem.casefold()]
    except OSError:
        return []

    related: list[Path] = []
    for candidate in candidates:
        if candidate == file_path:
            continue
        related.append(candidate)

    related.sort(key=lambda item: str(item).casefold())
    return related


def protect_duplicate_execution_preview(preview: DuplicateExecutionPreview) -> DuplicateExecutionPreview:
    rows: list[ExecutionPreviewRow] = []
    blocked_for_associated = 0

    for row in preview.rows:
        if row.row_type == "filesystem_delete" and row.status == "executable":
            associated_siblings = find_associated_sibling_paths(row.source_path)
            if associated_siblings:
                blocked_for_associated += 1
                rows.append(
                    ExecutionPreviewRow(
                        row_type="blocked_associated_files",
                        status="blocked",
                        group_id=row.group_id,
                        operation_mode=row.operation_mode,
                        source_path=row.source_path,
                        survivor_path=row.survivor_path,
                        target_path=row.target_path,
                        file_size=row.file_size,
                        reason="associated_files_present",
                    )
                )
                continue

        rows.append(row)

    return DuplicateExecutionPreview(
        ready=preview.ready and blocked_for_associated == 0,
        rows=rows,
    )
