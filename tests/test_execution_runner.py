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



def test_run_duplicate_execution_preview_in_preview_mode(tmp_path: Path) -> None:
    keep = tmp_path / "keep.jpg"
    remove = tmp_path / "remove.jpg"
    keep.write_bytes(b"keep-bytes")
    remove.write_bytes(b"remove-bytes")

    group = _group([keep, remove], file_size=11, digest="delete-preview")
    decision = {build_exact_group_id(group): str(keep)}

    dry_run = build_exact_cleanup_dry_run([group], decision, "delete")
    preview = build_duplicate_execution_preview(dry_run)
    result = run_duplicate_execution_preview(preview, apply=False)

    assert result.processed_rows == 1
    assert result.executable_rows == 1
    assert result.executed_rows == 1
    assert result.error_rows == 0
    assert result.entries[0].outcome == "preview-delete"
    assert remove.exists()



def test_run_duplicate_execution_preview_applies_delete(tmp_path: Path) -> None:
    keep = tmp_path / "keep.jpg"
    remove = tmp_path / "remove.jpg"
    keep.write_bytes(b"keep-bytes")
    remove.write_bytes(b"remove-bytes")

    group = _group([keep, remove], file_size=11, digest="delete-apply")
    decision = {build_exact_group_id(group): str(keep)}

    dry_run = build_exact_cleanup_dry_run([group], decision, "delete")
    preview = build_duplicate_execution_preview(dry_run)
    result = run_duplicate_execution_preview(preview, apply=True)

    assert result.processed_rows == 1
    assert result.executable_rows == 1
    assert result.executed_rows == 1
    assert result.error_rows == 0
    assert result.entries[0].outcome == "deleted"
    assert not remove.exists()
    assert keep.exists()



def test_run_duplicate_execution_preview_keeps_move_rows_deferred(tmp_path: Path) -> None:
    keep = tmp_path / "keep.jpg"
    remove = tmp_path / "remove.jpg"
    keep.write_bytes(b"keep-bytes")
    remove.write_bytes(b"remove-bytes")

    group = _group([keep, remove], file_size=11, digest="move")
    decision = {build_exact_group_id(group): str(keep)}

    dry_run = build_exact_cleanup_dry_run([group], decision, "move", target_root=tmp_path / "target")
    preview = build_duplicate_execution_preview(dry_run)
    result = run_duplicate_execution_preview(preview, apply=True)

    assert result.processed_rows == 1
    assert result.deferred_rows == 1
    assert result.executed_rows == 0
    assert result.error_rows == 0
    assert result.entries[0].outcome == "deferred"
    assert remove.exists()



def test_run_duplicate_execution_preview_preserves_blocked_rows(tmp_path: Path) -> None:
    first = tmp_path / "one.jpg"
    second = tmp_path / "two.jpg"
    first.write_bytes(b"one")
    second.write_bytes(b"two")

    group = _group([first, second], file_size=3, digest="blocked")
    dry_run = build_exact_cleanup_dry_run([group], {}, "delete")
    preview = build_duplicate_execution_preview(dry_run)
    result = run_duplicate_execution_preview(preview, apply=True)

    assert result.processed_rows == 2
    assert result.blocked_rows == 2
    assert result.executed_rows == 0
    assert result.error_rows == 0
    assert all(entry.outcome == "blocked" for entry in result.entries)
    assert first.exists()
    assert second.exists()



def test_run_duplicate_execution_preview_reports_missing_source_as_error(tmp_path: Path) -> None:
    keep = tmp_path / "keep.jpg"
    remove = tmp_path / "remove.jpg"
    keep.write_bytes(b"keep-bytes")
    remove.write_bytes(b"remove-bytes")

    group = _group([keep, remove], file_size=11, digest="missing")
    decision = {build_exact_group_id(group): str(keep)}

    dry_run = build_exact_cleanup_dry_run([group], decision, "delete")
    preview = build_duplicate_execution_preview(dry_run)

    remove.unlink()
    result = run_duplicate_execution_preview(preview, apply=True)

    assert result.processed_rows == 1
    assert result.executable_rows == 1
    assert result.executed_rows == 0
    assert result.error_rows == 1
    assert result.entries[0].outcome == "error"
    assert result.entries[0].reason == "source_missing"
