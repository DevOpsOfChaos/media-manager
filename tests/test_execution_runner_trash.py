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


def test_run_duplicate_execution_preview_uses_preview_delete_outcome(tmp_path: Path) -> None:
    keep = tmp_path / "keep.jpg"
    remove = tmp_path / "remove.jpg"
    keep.write_bytes(b"keep")
    remove.write_bytes(b"remove")

    group = _group([keep, remove], file_size=6, digest="preview-trash")
    decisions = {build_exact_group_id(group): str(keep)}
    dry_run = build_exact_cleanup_dry_run([group], decisions, "delete")
    preview = build_duplicate_execution_preview(dry_run)

    result = run_duplicate_execution_preview(preview, apply=False)

    assert result.executed_rows == 1
    assert result.error_rows == 0
    assert result.entries[0].outcome == "preview-delete"
    assert remove.exists()


def test_run_duplicate_execution_preview_marks_delete_as_deleted_after_trash(monkeypatch, tmp_path: Path) -> None:
    keep = tmp_path / "keep.jpg"
    remove = tmp_path / "remove.jpg"
    keep.write_bytes(b"keep")
    remove.write_bytes(b"remove")

    trashed: list[str] = []

    def fake_send2trash(path_str: str) -> None:
        trashed.append(path_str)
        Path(path_str).unlink()

    monkeypatch.setattr("media_manager.execution_runner.send2trash", fake_send2trash)

    group = _group([keep, remove], file_size=6, digest="apply-trash")
    decisions = {build_exact_group_id(group): str(keep)}
    dry_run = build_exact_cleanup_dry_run([group], decisions, "delete")
    preview = build_duplicate_execution_preview(dry_run)

    result = run_duplicate_execution_preview(preview, apply=True)

    assert result.executed_rows == 1
    assert result.error_rows == 0
    assert result.entries[0].outcome == "deleted"
    assert trashed == [str(remove)]
    assert not remove.exists()
    assert keep.exists()
