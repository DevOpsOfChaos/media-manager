from __future__ import annotations

from pathlib import Path

from media_manager.cleanup_plan import build_exact_cleanup_dry_run, build_exact_group_id
from media_manager.duplicates import ExactDuplicateGroup
from media_manager.execution_plan import build_duplicate_execution_preview
from media_manager.execution_runner import run_duplicate_execution_preview


def _group(paths: list[Path], file_size: int = 1234, digest: str = "digest") -> ExactDuplicateGroup:
    return ExactDuplicateGroup(
        files=paths,
        file_size=file_size,
        sample_digest="sample",
        full_digest=digest,
        same_name=False,
        same_suffix=True,
    )


def test_run_duplicate_execution_preview_blocks_when_survivor_is_missing(tmp_path: Path) -> None:
    keep = tmp_path / "keep.jpg"
    remove = tmp_path / "remove.jpg"
    keep.write_bytes(b"keep-bytes")
    remove.write_bytes(b"remove-bytes")

    group = _group([keep, remove], file_size=11, digest="missing-survivor")
    decision = {build_exact_group_id(group): str(keep)}

    dry_run = build_exact_cleanup_dry_run([group], decision, "delete")
    preview = build_duplicate_execution_preview(dry_run)

    keep.unlink()
    result = run_duplicate_execution_preview(preview, apply=True)

    assert result.processed_rows == 1
    assert result.executable_rows == 1
    assert result.executed_rows == 0
    assert result.blocked_rows == 1
    assert result.blocked_missing_survivor_rows == 1
    assert result.error_rows == 0
    assert result.entries[0].outcome == "blocked"
    assert result.entries[0].reason == "survivor_missing"
    assert remove.exists()


def test_run_duplicate_execution_preview_exposes_preview_and_delete_counters(tmp_path: Path) -> None:
    keep = tmp_path / "keep.jpg"
    remove = tmp_path / "remove.jpg"
    keep.write_bytes(b"keep-bytes")
    remove.write_bytes(b"remove-bytes")

    group = _group([keep, remove], file_size=11, digest="preview-counts")
    decision = {build_exact_group_id(group): str(keep)}

    dry_run = build_exact_cleanup_dry_run([group], decision, "delete")
    preview = build_duplicate_execution_preview(dry_run)

    preview_result = run_duplicate_execution_preview(preview, apply=False)
    assert preview_result.executed_rows == 1
    assert preview_result.previewed_rows == 1
    assert preview_result.deleted_rows == 0
    assert remove.exists()

    apply_result = run_duplicate_execution_preview(preview, apply=True)
    assert apply_result.executed_rows == 1
    assert apply_result.previewed_rows == 0
    assert apply_result.deleted_rows == 1
